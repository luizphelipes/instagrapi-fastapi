import logging
import os
import random
import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import BadPassword, TwoFactorRequired, ChallengeRequired, FeedbackRequired

from services.redis_cache import redis_cache
from database import InstagramAccount

load_dotenv()

logger = logging.getLogger(__name__)

# iPhone device settings (consider moving to a config file)
IPHONE_DEVICES = [
    {
        "app_version": "219.0.0.12.117",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "640dpi",
        "resolution": "1440x2560",
        "manufacturer": "OnePlus",
        "device": "ONEPLUS A3003",
        "model": "OnePlus3",
        "cpu": "qcom",
        "version_code": "314665256",
        "user_agent": "Instagram 219.0.0.12.117 Android (26/8.0.0; 640dpi; 1440x2560; OnePlus; ONEPLUS A3003; OnePlus3; qcom; en_US; 314665256)"
    }
]

class AccountManager:
    """
    Gerenciador de contas com sistema de pré-aquecimento e monitoramento.
    """
    
    def __init__(self, service_instance):
        self.service = service_instance  # Referência para o InstagramService
        self.accounts_status: Dict[str, Dict] = {}
        self.last_activity: Dict[str, datetime] = {}
        self.warmup_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self.warmup_logs: List[Dict] = []  # Logs detalhados do pré-aquecimento
        self.max_logs = 1000  # Máximo de logs mantidos
        
    def _add_log(self, account_id: str, activity: str, status: str, details: str = None, duration: float = None):
        """Adiciona um log de atividade"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "account_id": account_id,
            "activity": activity,
            "status": status,
            "details": details,
            "duration": duration
        }
        
        self.warmup_logs.append(log_entry)
        
        # Mantém apenas os últimos max_logs
        if len(self.warmup_logs) > self.max_logs:
            self.warmup_logs = self.warmup_logs[-self.max_logs:]
        
        # Log para console também
        emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        logger.info(f"{emoji} [{account_id}] {activity}: {status} {f'({details})' if details else ''} {f'[{duration:.2f}s]' if duration else ''}")
        
    async def start_warmup_system(self):
        """Inicia o sistema de pré-aquecimento para todas as contas"""
        if self.is_running:
            logger.info("Sistema de pré-aquecimento já está rodando")
            return
            
        self.is_running = True
        self._add_log("SYSTEM", "Warmup System Start", "success", f"Starting warmup for {len(self.accounts_status)} accounts")
        logger.info("🚀 Iniciando sistema de pré-aquecimento de contas")
        
        # Inicia tarefas de pré-aquecimento para cada conta
        for account_id in self.accounts_status.keys():
            await self.start_account_warmup(account_id)
    
    async def stop_warmup_system(self):
        """Para o sistema de pré-aquecimento"""
        self.is_running = False
        self._add_log("SYSTEM", "Warmup System Stop", "success", f"Stopping {len(self.warmup_tasks)} warmup tasks")
        logger.info("🛑 Parando sistema de pré-aquecimento de contas")
        
        # Cancela todas as tarefas de pré-aquecimento
        for task in self.warmup_tasks.values():
            if not task.done():
                task.cancel()
        
        self.warmup_tasks.clear()
    
    async def start_account_warmup(self, account_id: str):
        """Inicia pré-aquecimento para uma conta específica"""
        if account_id in self.warmup_tasks and not self.warmup_tasks[account_id].done():
            self._add_log(account_id, "Warmup Start", "warning", "Warmup already active")
            logger.info(f"Pré-aquecimento já ativo para conta {account_id}")
            return
            
        task = asyncio.create_task(self._account_warmup_loop(account_id))
        self.warmup_tasks[account_id] = task
        self._add_log(account_id, "Warmup Start", "success", "Warmup task created")
        logger.info(f"🔥 Iniciado pré-aquecimento para conta {account_id}")
    
    async def stop_account_warmup(self, account_id: str):
        """Para pré-aquecimento de uma conta específica"""
        if account_id in self.warmup_tasks:
            task = self.warmup_tasks[account_id]
            if not task.done():
                task.cancel()
                self._add_log(account_id, "Warmup Stop", "success", "Warmup task cancelled")
                logger.info(f"🛑 Parado pré-aquecimento para conta {account_id}")
            del self.warmup_tasks[account_id]
    
    async def _account_warmup_loop(self, account_id: str):
        """Loop principal de pré-aquecimento para uma conta"""
        while self.is_running:
            try:
                # Intervalo variável entre 15-45 minutos
                interval = random.randint(15, 45) * 60
                self._add_log(account_id, "Warmup Schedule", "info", f"Next warmup in {interval//60} minutes")
                logger.info(f"⏰ Próximo pré-aquecimento para {account_id} em {interval//60} minutos")
                
                await asyncio.sleep(interval)
                
                if not self.is_running:
                    break
                    
                # Executa atividade de pré-aquecimento
                await self._perform_warmup_activity(account_id)
                
            except asyncio.CancelledError:
                self._add_log(account_id, "Warmup Cancelled", "info", "Warmup loop cancelled")
                logger.info(f"🛑 Pré-aquecimento cancelado para conta {account_id}")
                break
            except Exception as e:
                self._add_log(account_id, "Warmup Error", "error", f"Loop error: {str(e)}")
                logger.error(f"❌ Erro no pré-aquecimento da conta {account_id}: {e}")
                await asyncio.sleep(300)  # Espera 5 minutos antes de tentar novamente
    
    async def _perform_warmup_activity(self, account_id: str):
        """Executa uma atividade de pré-aquecimento aleatória"""
        try:
            client = self._get_client_for_account(account_id)
            if not client:
                self._add_log(account_id, "Client Creation", "error", "Client not available")
                logger.warning(f"⚠️ Cliente não disponível para pré-aquecimento da conta {account_id}")
                return
            
            # Escolhe uma atividade aleatória
            activities = [
                self._browse_feed,
                self._explore_page,
                self._view_stories,
                self._like_random_post,
                self._follow_suggestions
            ]
            
            activity = random.choice(activities)
            activity_name = activity.__name__.replace('_', ' ').title()
            
            self._add_log(account_id, "Activity Start", "info", f"Starting {activity_name}")
            logger.info(f"🎯 Executando {activity_name} para conta {account_id}")
            
            start_time = time.time()
            await activity(client, account_id)
            duration = time.time() - start_time
            
            # Atualiza status da conta
            self.accounts_status[account_id] = {
                "last_warmup": datetime.utcnow(),
                "last_activity": activity_name,
                "warmup_duration": duration,
                "status": "active"
            }
            
            self._add_log(account_id, activity_name, "success", f"Completed successfully", duration)
            logger.info(f"✅ {activity_name} concluído para {account_id} em {duration:.2f}s")
            
        except Exception as e:
            self._add_log(account_id, "Activity Error", "error", f"Error: {str(e)}")
            logger.error(f"❌ Erro na atividade de pré-aquecimento para {account_id}: {e}")
            self.accounts_status[account_id] = {
                "last_warmup": datetime.utcnow(),
                "last_activity": "error",
                "error": str(e),
                "status": "error"
            }
    
    def _get_client_for_account(self, account_id: str) -> Optional[Client]:
        """Obtém cliente específico para uma conta"""
        session_id = self.service._session_ids.get(account_id)
        if not session_id:
            return None
            
        if account_id in self.service._clients:
            return self.service._clients[account_id]
        
        try:
            client = Client(request_timeout=15)
            device = random.choice(IPHONE_DEVICES)
            client.set_device(device)
            client.set_user_agent(device["user_agent"])
            client.login_by_sessionid(session_id)
            self.service._clients[account_id] = client
            self._add_log(account_id, "Client Creation", "success", "New client created")
            return client
        except Exception as e:
            self._add_log(account_id, "Client Creation", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao criar cliente para pré-aquecimento da conta {account_id}: {e}")
            return None
    
    async def _browse_feed(self, client: Client, account_id: str):
        """Navega pelo feed principal"""
        try:
            # Obtém algumas postagens do feed
            feed = client.feed_timeline(amount=random.randint(3, 8))
            
            likes_given = 0
            # Simula tempo de visualização variável
            for post in feed:
                view_time = random.uniform(2.0, 8.0)
                await asyncio.sleep(view_time)
                
                # Ocasionalmente curte uma postagem (10% de chance)
                if random.random() < 0.1:
                    try:
                        client.media_like(post.id)
                        likes_given += 1
                        self._add_log(account_id, "Feed Like", "success", f"Liked post {post.id}")
                        await asyncio.sleep(random.uniform(1.0, 3.0))
                    except Exception as e:
                        self._add_log(account_id, "Feed Like", "error", f"Error liking post {post.id}: {str(e)}")
            
            self._add_log(account_id, "Feed Browse", "success", f"Viewed {len(feed)} posts, gave {likes_given} likes")
            logger.info(f"📱 Feed navegado pela conta {account_id} - {len(feed)} posts visualizados, {likes_given} likes")
            
        except Exception as e:
            self._add_log(account_id, "Feed Browse", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao navegar feed para {account_id}: {e}")
    
    async def _explore_page(self, client: Client, account_id: str):
        """Navega pela página de exploração"""
        try:
            # Obtém posts da página de exploração
            explore = client.explore_feed(amount=random.randint(5, 12))
            
            saves_given = 0
            for post in explore:
                view_time = random.uniform(1.5, 6.0)
                await asyncio.sleep(view_time)
                
                # Ocasionalmente salva uma postagem (5% de chance)
                if random.random() < 0.05:
                    try:
                        client.media_save(post.id)
                        saves_given += 1
                        self._add_log(account_id, "Explore Save", "success", f"Saved post {post.id}")
                        await asyncio.sleep(random.uniform(1.0, 2.0))
                    except Exception as e:
                        self._add_log(account_id, "Explore Save", "error", f"Error saving post {post.id}: {str(e)}")
            
            self._add_log(account_id, "Explore Browse", "success", f"Viewed {len(explore)} posts, saved {saves_given} posts")
            logger.info(f"🔍 Página de exploração navegada pela conta {account_id} - {len(explore)} posts visualizados, {saves_given} salvos")
            
        except Exception as e:
            self._add_log(account_id, "Explore Browse", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao navegar exploração para {account_id}: {e}")
    
    async def _view_stories(self, client: Client, account_id: str):
        """Visualiza stories de usuários"""
        try:
            # Obtém stories do feed
            stories = client.story_feed(amount=random.randint(3, 8))
            
            reactions_given = 0
            for story in stories:
                view_time = random.uniform(1.0, 4.0)
                await asyncio.sleep(view_time)
                
                # Ocasionalmente responde a um story (3% de chance)
                if random.random() < 0.03:
                    try:
                        emoji = random.choice(['❤️', '🔥', '👍', '😍', '👏'])
                        client.story_react(story.id, emoji)
                        reactions_given += 1
                        self._add_log(account_id, "Story Reaction", "success", f"Reacted '{emoji}' to story {story.id}")
                        await asyncio.sleep(random.uniform(1.0, 2.0))
                    except Exception as e:
                        self._add_log(account_id, "Story Reaction", "error", f"Error reacting to story {story.id}: {str(e)}")
            
            self._add_log(account_id, "Story View", "success", f"Viewed {len(stories)} stories, gave {reactions_given} reactions")
            logger.info(f"📸 Stories visualizados pela conta {account_id} - {len(stories)} stories vistos, {reactions_given} reações")
            
        except Exception as e:
            self._add_log(account_id, "Story View", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao visualizar stories para {account_id}: {e}")
    
    async def _like_random_post(self, client: Client, account_id: str):
        """Curti uma postagem aleatória de um usuário popular"""
        try:
            # Lista de usuários populares para interagir
            popular_users = [
                'instagram', 'natgeo', 'nike', 'adidas', 'starbucks',
                'coca_cola', 'mcdonalds', 'netflix', 'spotify', 'youtube'
            ]
            
            user = random.choice(popular_users)
            
            # Obtém posts do usuário
            user_id = client.user_id_from_username(user)
            posts = client.user_medias(user_id, amount=random.randint(1, 3))
            
            likes_given = 0
            for post in posts:
                # Simula tempo de visualização
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
                # Curti a postagem
                try:
                    client.media_like(post.id)
                    likes_given += 1
                    self._add_log(account_id, "Popular Like", "success", f"Liked post from @{user}")
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                except Exception as e:
                    self._add_log(account_id, "Popular Like", "error", f"Error liking post from @{user}: {str(e)}")
            
            self._add_log(account_id, "Popular Interaction", "success", f"Interacted with @{user}, gave {likes_given} likes")
            logger.info(f"👍 Like dado em post de @{user} pela conta {account_id}")
            
        except Exception as e:
            self._add_log(account_id, "Popular Interaction", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao curtir post aleatório para {account_id}: {e}")
    
    async def _follow_suggestions(self, client: Client, account_id: str):
        """Interage com sugestões de seguir"""
        try:
            # Obtém sugestões de seguir
            suggestions = client.user_suggestions(amount=random.randint(3, 6))
            
            follows_given = 0
            for user in suggestions:
                # Simula tempo de análise do perfil
                await asyncio.sleep(random.uniform(3.0, 8.0))
                
                # Ocasionalmente segue um usuário (2% de chance)
                if random.random() < 0.02:
                    try:
                        client.user_follow(user.pk)
                        follows_given += 1
                        self._add_log(account_id, "Follow Suggestion", "success", f"Followed @{user.username}")
                        await asyncio.sleep(random.uniform(2.0, 5.0))
                    except Exception as e:
                        self._add_log(account_id, "Follow Suggestion", "error", f"Error following @{user.username}: {str(e)}")
            
            self._add_log(account_id, "Suggestion Analysis", "success", f"Analyzed {len(suggestions)} users, followed {follows_given}")
            logger.info(f"👤 Sugestões analisadas pela conta {account_id} - {len(suggestions)} usuários vistos, {follows_given} seguidos")
            
        except Exception as e:
            self._add_log(account_id, "Suggestion Analysis", "error", f"Error: {str(e)}")
            logger.error(f"Erro ao analisar sugestões para {account_id}: {e}")
    
    def get_account_status(self, account_id: str) -> Dict:
        """Retorna status detalhado de uma conta"""
        return self.accounts_status.get(account_id, {})
    
    def get_all_accounts_status(self) -> Dict:
        """Retorna status de todas as contas"""
        return {
            "total_accounts": len(self.accounts_status),
            "active_accounts": len([acc for acc in self.accounts_status.values() if acc.get("status") == "active"]),
            "error_accounts": len([acc for acc in self.accounts_status.values() if acc.get("status") == "error"]),
            "warmup_tasks": len(self.warmup_tasks),
            "system_running": self.is_running,
            "accounts": self.accounts_status
        }
    
    def get_warmup_logs(self, limit: int = 100) -> List[Dict]:
        """Retorna logs de pré-aquecimento"""
        return self.warmup_logs[-limit:] if limit > 0 else self.warmup_logs 

class InstagramService:
    """
    Serviço para interagir com o Instagram, com cache Redis, rotação de contas e sistema de pré-aquecimento.
    Versão async para FastAPI com otimizações para reduzir cold start.
    """

    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._session_ids: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._account_ids: List[str] = []
        self._account_index = 0
        self.account_manager = AccountManager(self) # Passa a instância do serviço
        self._initialized = False
        self._init_task = None

    async def initialize(self, db: AsyncSession = None):
        """Inicializa o serviço de forma assíncrona"""
        if self._initialized:
            return
            
        logger.info("🚀 Inicializando InstagramService...")
        start_time = time.time()
        
        # Carrega contas do .env
        await self._load_from_env()
        
        # Carrega contas do banco se disponível
        if db:
            await self._load_session_ids(db)
        
        # Pré-inicializa pelo menos um cliente
        if self._account_ids:
            try:
                account_id = self._account_ids[0]
                await self._initialize_client(account_id)
                logger.info(f"✅ Cliente pré-inicializado para {account_id}")
            except Exception as e:
                logger.error(f"❌ Erro na pré-inicialização: {e}")
        
        # Inicia sistema de pré-aquecimento
        if self._account_ids:
            await self.account_manager.start_warmup_system()
        
        self._initialized = True
        logger.info(f"✅ InstagramService inicializado em {time.time() - start_time:.2f}s")

    async def ensure_initialized(self):
        """Garante que o serviço está inicializado"""
        if not self._initialized:
            await self.initialize()

    async def _pre_initialize(self):
        """Pré-inicializa os clientes para reduzir cold start"""
        if self._initialized:
            return
            
        logger.info("🚀 Iniciando pré-inicialização dos clientes Instagram...")
        start_time = time.time()
        
        # Carrega contas do .env primeiro
        await self._load_from_env()
        
        # Pré-inicializa pelo menos um cliente
        if self._account_ids:
            try:
                account_id = self._account_ids[0]
                await self._initialize_client(account_id)
                logger.info(f"✅ Cliente pré-inicializado para {account_id} em {time.time() - start_time:.2f}s")
            except Exception as e:
                logger.error(f"❌ Erro na pré-inicialização: {e}")
        
        self._initialized = True

    async def _load_from_env(self):
        """Carrega contas do arquivo .env"""
        for key, value in os.environ.items():
            if key.startswith('INSTAGRAM_SESSION_ID_') and value:
                account_id = key.replace('INSTAGRAM_SESSION_ID_', '')
                if account_id not in self._session_ids:
                    self._session_ids[account_id] = value
                    self.account_manager.accounts_status[account_id] = {
                        "username": account_id,
                        "last_synced": datetime.utcnow().isoformat(),
                        "status": "loaded",
                        "last_warmup": None,
                        "last_activity": None
                    }
                    logger.info(f"Conta {account_id} carregada do .env.")
        
        self._account_ids = list(self._session_ids.keys())

    async def _initialize_client(self, account_id: str) -> Optional[Client]:
        """Inicializa um cliente específico"""
        session_id = self._session_ids.get(account_id)
        if not session_id:
            logger.error(f"Session ID não encontrado para a conta {account_id}")
            return None
        
        try:
            client = Client(request_timeout=10)  # Reduzido de 15 para 10
            device = random.choice(IPHONE_DEVICES)
            client.set_device(device)
            client.set_user_agent(device["user_agent"])
            client.login_by_sessionid(session_id)
            self._clients[account_id] = client
            logger.info(f"Cliente Instagrapi criado para a conta {account_id}")
            return client
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente para conta {account_id}: {e}")
            # Remove conta inválida
            if account_id in self._session_ids:
                del self._session_ids[account_id]
            if account_id in self._account_ids:
                self._account_ids.remove(account_id)
            return None

    async def _load_session_ids(self, db: AsyncSession):
        """Carrega os session IDs das contas do banco de dados e do arquivo .env."""
        try:
            # Carrega do banco de dados
            result = await db.execute(select(InstagramAccount))
            accounts = result.scalars().all()
            
            for account in accounts:
                try:
                    self._session_ids[account.username] = account.session_id
                    # Inicializa status da conta no manager
                    self.account_manager.accounts_status[account.username] = {
                        "username": account.username,
                        "last_synced": account.last_synced.isoformat() if account.last_synced else None,
                        "status": "loaded",
                        "last_warmup": None,
                        "last_activity": None
                    }
                    logger.info(f"Conta {account.username} carregada do banco de dados.")
                except Exception as e:
                    logger.error(f"Erro ao descriptografar session_id para {account.username}: {e}")

            # Carrega do arquivo .env
            for key, value in os.environ.items():
                if key.startswith('INSTAGRAM_SESSION_ID_') and value:
                    account_id = key.replace('INSTAGRAM_SESSION_ID_', '')
                    if account_id not in self._session_ids:
                        self._session_ids[account_id] = value
                        self.account_manager.accounts_status[account_id] = {
                            "username": account_id,
                            "last_synced": datetime.utcnow().isoformat(),
                            "status": "loaded",
                            "last_warmup": None,
                            "last_activity": None
                        }
                        logger.info(f"Conta {account_id} carregada do .env.")

            self._account_ids = list(self._session_ids.keys())
            logger.info(f"{len(self._session_ids)} contas do Instagram carregadas no total.")
            
            # Inicia sistema de pré-aquecimento
            await self.account_manager.start_warmup_system()
            
        except Exception as e:
            logger.error(f"Erro ao carregar session IDs: {e}")

    async def _update_accounts_from_db(self, db: AsyncSession):
        """Atualiza as contas do banco de dados no cache local"""
        try:
            result = await db.execute(select(InstagramAccount))
            accounts = result.scalars().all()
            
            for account in accounts:
                try:
                    if account.username not in self._session_ids:
                        self._session_ids[account.username] = account.session_id
                        # Adiciona ao manager de contas
                        self.account_manager.accounts_status[account.username] = {
                            "username": account.username,
                            "last_synced": account.last_synced.isoformat() if account.last_synced else None,
                            "status": "loaded",
                            "last_warmup": None,
                            "last_activity": None
                        }
                        logger.info(f"Conta {account.username} carregada do banco de dados.")
                        
                        # Inicia pré-aquecimento para nova conta
                        await self.account_manager.start_account_warmup(account.username)
                except Exception as e:
                    logger.error(f"Erro ao carregar session_id para {account.username}: {e}")

            # Atualiza a lista de account_ids
            self._account_ids = list(self._session_ids.keys())
            logger.info(f"Total de {len(self._session_ids)} contas carregadas.")
            
        except Exception as e:
            logger.error(f"Erro ao carregar contas do banco de dados: {e}")

    async def _get_next_account_id(self) -> Optional[str]:
        """Seleciona a próxima conta disponível (round-robin, thread-safe)."""
        async with self._lock:
            if not self._account_ids:
                logger.error("Nenhuma conta Instagram configurada!")
                return None
            account_id = self._account_ids[self._account_index]
            self._account_index = (self._account_index + 1) % len(self._account_ids)
            return account_id

    def _get_client(self) -> Optional[Client]:
        """
        Obtém ou cria um cliente Instagrapi para a próxima conta disponível (Lazy Loading otimizado).
        """
        # Se não há contas carregadas, tenta carregar do .env primeiro
        if not self._account_ids:
            # Carrega do arquivo .env
            for key, value in os.environ.items():
                if key.startswith('INSTAGRAM_SESSION_ID_') and value:
                    account_id = key.replace('INSTAGRAM_SESSION_ID_', '')
                    if account_id not in self._session_ids:
                        self._session_ids[account_id] = value
                        self.account_manager.accounts_status[account_id] = {
                            "username": account_id,
                            "last_synced": datetime.utcnow().isoformat(),
                            "status": "loaded",
                            "last_warmup": None,
                            "last_activity": None
                        }
                        logger.info(f"Conta {account_id} carregada do .env.")
            
            self._account_ids = list(self._session_ids.keys())
            
            if not self._account_ids:
                logger.error("Nenhuma conta Instagram configurada!")
                return None
            
            logger.info(f"{len(self._session_ids)} contas do Instagram carregadas do .env.")
            
        account_id = self._account_ids[self._account_index]
        self._account_index = (self._account_index + 1) % len(self._account_ids)

        # Se o cliente já existe no pool, retorna ele
        if account_id in self._clients:
            return self._clients[account_id]

        # Se não, cria um novo cliente (Lazy Loading)
        session_id = self._session_ids.get(account_id)
        if not session_id:
            logger.error(f"Session ID não encontrado para a conta {account_id}")
            return None
        
        try:
            client = Client(request_timeout=10)  # Reduzido de 15 para 10
            device = random.choice(IPHONE_DEVICES)
            client.set_device(device)
            client.set_user_agent(device["user_agent"])
            client.login_by_sessionid(session_id)
            self._clients[account_id] = client
            logger.info(f"Cliente Instagrapi criado para a conta {account_id}")
            return client
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente para conta {account_id}: {e}")
            # Remove conta inválida
            if account_id in self._session_ids:
                del self._session_ids[account_id]
            if account_id in self._account_ids:
                self._account_ids.remove(account_id)
            return None

    def _find_user_id(self, client: Client, username: str) -> Optional[int]:
        """
        Busca o user_id de forma otimizada usando search_users.
        Retorna None se não encontrar.
        """
        try:
            # Busca usuários com o username específico
            resultados = client.search_users(query=username)
            
            # Filtra pelo username exato (case-insensitive)
            username_lower = username.lower()
            for user in resultados:
                if user.username.lower() == username_lower:
                    return user.pk
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar user_id para {username}: {e}")
            return None

    @redis_cache(ttl=300)  # Cache de 5 minutos
    async def get_user_stories(self, username: str, db: AsyncSession = None) -> dict:
        """Obtém os stories de um usuário."""
        # Garante que o serviço está inicializado
        await self.ensure_initialized()
        
        # Se não há contas carregadas e temos acesso ao banco, tenta carregar
        if not self._account_ids and db:
            await self._update_accounts_from_db(db)
            
        client = self._get_client()
        if not client:
            return {"status": "error", "message": "No available Instagram accounts"}
        try:
            # Busca o user_id de forma otimizada
            user_id = self._find_user_id(client, username)
            if user_id is None:
                return {"status": "error", "message": "User not found"}
            
            # Tenta obter os stories com tratamento de erro específico
            try:
                stories = client.user_stories(user_id)
                
                stories_data = []
                for story in stories:
                    stories_data.append({
                        "id": story.id,
                        "code": story.code,
                        "taken_at": story.taken_at.isoformat(),
                        "media_type": story.media_type,
                        "video_url": str(story.video_url) if story.video_url else None,
                        "thumbnail_url": str(story.thumbnail_url) if story.thumbnail_url else None,
                    })
                return {"status": "success", "stories": stories_data}
            except KeyError as e:
                if 'data' in str(e):
                    logger.warning(f"Instagram API retornou resposta inesperada para stories de {username}.")
                    return {"status": "error", "message": "Failed to retrieve stories - API response error"}
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Erro ao buscar stories de {username}: {e}")
            return {"status": "error", "message": f"Failed to retrieve stories for {username}"}

    @redis_cache(ttl=120)  # Cache de 2 minutos
    async def get_profile_privacy(self, username: str, db: AsyncSession = None) -> dict:
        # Garante que o serviço está inicializado
        await self.ensure_initialized()
        
        # Se não há contas carregadas e temos acesso ao banco, tenta carregar
        if not self._account_ids and db:
            await self._update_accounts_from_db(db)
            
        client = self._get_client()
        if not client:
            return {"status": "error", "message": "No available Instagram accounts"}
        try:
            # Busca o user_id de forma otimizada
            user_id = self._find_user_id(client, username)
            if user_id is None:
                return {"status": "error", "message": "User not found"}
            
            # Obtém as informações usando o user_id
            user_info = client.user_info(user_id)
            if not user_info:
                return {"status": "error", "message": "User not found"}
                
            privacy = "private" if user_info.is_private else "public"
            return {"status": "success", "privacy": privacy, "source": "instagrapi"}
        except Exception as e:
            logger.error(f"Erro ao verificar perfil {username} com Instagrapi: {e}")
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                return {"status": "error", "message": "User not found"}
            return {"status": "error", "message": "Failed to retrieve profile privacy"}

    @redis_cache(ttl=1800)  # Cache de 30 minutos
    async def get_last_posts(self, username: str, count: int = 4, db: AsyncSession = None) -> dict:
        # Se não há contas carregadas e temos acesso ao banco, tenta carregar
        if not self._account_ids and db:
            await self._update_accounts_from_db(db)
            
        client = self._get_client()
        if not client:
            return {"status": "error", "message": "No available Instagram accounts"}
        try:
            # Busca o user_id de forma otimizada
            user_id = self._find_user_id(client, username)
            if user_id is None:
                return {"status": "error", "message": "User not found"}
            
            # Tenta obter as mídias com tratamento de erro específico
            try:
                medias = client.user_medias(user_id, amount=count)
                post_codes = [media.code for media in medias]
                return {"status": "success", "posts": post_codes, "source": "instagrapi"}
            except KeyError as e:
                if 'data' in str(e):
                    logger.warning(f"Instagram API retornou resposta inesperada para posts de {username}. Tentando método alternativo.")
                    # Tenta método alternativo
                    try:
                        medias = client.user_medias_v1(user_id, amount=count)
                        post_codes = [media.code for media in medias]
                        return {"status": "success", "posts": post_codes, "source": "instagrapi"}
                    except Exception as e2:
                        logger.error(f"Erro no método alternativo para posts de {username}: {e2}")
                        return {"status": "error", "message": "Failed to retrieve posts - API response error"}
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Erro ao buscar posts de {username} com Instagrapi: {e}")
            return {"status": "error", "message": "Failed to retrieve posts"}

    @redis_cache(ttl=1800)  # Cache de 30 minutos
    async def get_last_reels(self, username: str, count: int = 4, db: AsyncSession = None) -> dict:
        # Se não há contas carregadas e temos acesso ao banco, tenta carregar
        if not self._account_ids and db:
            await self._update_accounts_from_db(db)
            
        client = self._get_client()
        if not client:
            return {"status": "error", "message": "No available Instagram accounts"}
        try:
            # Busca o user_id de forma otimizada
            user_id = self._find_user_id(client, username)
            if user_id is None:
                return {"status": "error", "message": "User not found"}
            
            # Tenta obter as mídias com tratamento de erro específico
            try:
                medias = client.user_medias(user_id, amount=20)
                reel_codes = [m.code for m in medias if m.product_type == "clips"][:count]
                return {"status": "success", "reels": reel_codes, "source": "instagrapi"}
            except KeyError as e:
                if 'data' in str(e):
                    logger.warning(f"Instagram API retornou resposta inesperada para reels de {username}. Tentando método alternativo.")
                    # Tenta método alternativo
                    try:
                        medias = client.user_medias_v1(user_id, amount=20)
                        reel_codes = [m.code for m in medias if hasattr(m, 'product_type') and m.product_type == "clips"][:count]
                        return {"status": "success", "reels": reel_codes, "source": "instagrapi"}
                    except Exception as e2:
                        logger.error(f"Erro no método alternativo para reels de {username}: {e2}")
                        return {"status": "error", "message": "Failed to retrieve reels - API response error"}
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Erro ao buscar reels de {username} com Instagrapi: {e}")
            return {"status": "error", "message": "Failed to retrieve reels"}

    @redis_cache(ttl=1800)  # Cache de 30 minutos
    async def get_profile_info(self, username: str, db: AsyncSession = None) -> dict:
        # Se não há contas carregadas e temos acesso ao banco, tenta carregar
        if not self._account_ids and db:
            await self._update_accounts_from_db(db)
            
        client = self._get_client()
        if not client:
            return {"status": "error", "message": "No available Instagram accounts"}
        try:
            # Busca o user_id de forma otimizada
            user_id = self._find_user_id(client, username)
            if user_id is None:
                return {"status": "error", "message": "User not found"}
            
            # Obtém as informações completas usando o user_id
            user_info = client.user_info(user_id)
            if not user_info:
                return {"status": "error", "message": "User not found"}
                
            data = {
                "username": user_info.username,
                "full_name": user_info.full_name,
                "biography": user_info.biography,
                "followers_count": user_info.follower_count,
                "following_count": user_info.following_count,
                "media_count": user_info.media_count,
                "is_private": user_info.is_private,
                "is_verified": user_info.is_verified,
                "is_business": user_info.is_business,
                "category": user_info.category_name,
                "profile_pic_url": str(user_info.profile_pic_url),
                "profile_pic_hd": str(user_info.profile_pic_url_hd),
                "external_url": str(user_info.external_url),
                "created_at": None,
                "last_updated": None
            }
            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f"Erro ao buscar informações do perfil {username} com Instagrapi: {e}")
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                return {"status": "error", "message": "User not found"}
            return {"status": "error", "message": "Failed to retrieve profile information"}

    async def login_and_save_account_by_session(self, session_id: str, db: AsyncSession) -> dict:
        client = Client(request_timeout=15)
        device = random.choice(IPHONE_DEVICES)
        client.set_device(device)
        client.set_user_agent(device["user_agent"])
        try:
            client.login_by_sessionid(session_id)
            user_id = client.user_id
            user_info = client.user_info(user_id)
            username = user_info.username
            if not user_info:
                return {"status": "error", "message": "Failed to retrieve user info after login with session_id."}
            
            # Verifica se a conta já existe
            result = await db.execute(select(InstagramAccount).where(InstagramAccount.username == username))
            account = result.scalar_one_or_none()
            
            if not account:
                account = InstagramAccount(username=username)
                db.add(account)

            account.session_id = session_id
            account.last_synced = datetime.utcnow()
            await db.commit()
            await db.refresh(account)
            
            logger.info(f"Conta {username} logada com session_id e salva/atualizada no banco de dados.")

            # Atualiza cache local
            self._session_ids[username] = session_id
            self._clients[username] = client
            if username not in self._account_ids:
                self._account_ids.append(username)

            return {"status": "success", "message": "Login with session_id successful and account saved.", "username": username}
        except Exception as e:
            logger.error(f"Erro ao tentar login com session_id: {e}")
            return {"status": "error", "message": f"An unexpected error occurred: {e}. The session_id may be invalid."}

    async def delete_account(self, username: str, db: AsyncSession) -> bool:
        try:
            result = await db.execute(select(InstagramAccount).where(InstagramAccount.username == username))
            account_to_delete = result.scalar_one_or_none()
            
            if not account_to_delete:
                return False

            await db.delete(account_to_delete)
            await db.commit()

            # Remove do cache local
            if username in self._session_ids:
                del self._session_ids[username]
            if username in self._clients:
                del self._clients[username]
            if username in self._account_ids:
                self._account_ids.remove(username)
            
            logger.info(f"Conta {username} deletada do sistema.")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar conta {username}: {e}")
            return False

    async def list_accounts(self, db: AsyncSession) -> List[dict]:
        """Lista todas as contas salvas no banco de dados."""
        try:
            result = await db.execute(select(InstagramAccount))
            accounts = result.scalars().all()
            
            accounts_data = []
            for acc in accounts:
                accounts_data.append({
                    "id": acc.id,
                    "username": acc.username,
                    "last_synced": acc.last_synced.isoformat() if acc.last_synced else None
                })
            
            return accounts_data
        except Exception as e:
            logger.error(f"Erro ao listar contas: {e}")
            return []

    # Métodos de gerenciamento de contas
    async def get_accounts_status(self) -> Dict:
        """Retorna status detalhado de todas as contas"""
        return self.account_manager.get_all_accounts_status()
    
    async def get_account_status(self, username: str) -> Dict:
        """Retorna status detalhado de uma conta específica"""
        return self.account_manager.get_account_status(username)
    
    async def start_account_warmup(self, username: str):
        """Inicia pré-aquecimento para uma conta específica"""
        await self.account_manager.start_account_warmup(username)
    
    async def stop_account_warmup(self, username: str):
        """Para pré-aquecimento de uma conta específica"""
        await self.account_manager.stop_account_warmup(username)
    
    async def stop_warmup_system(self):
        """Para o sistema de pré-aquecimento"""
        await self.account_manager.stop_warmup_system()
    
    async def get_warmup_logs(self, limit: int = 100) -> List[Dict]:
        """Retorna logs detalhados do sistema de pré-aquecimento"""
        return self.account_manager.get_warmup_logs(limit)

# Singleton para facilitar o acesso ao serviço
_instance = None
_instance_lock = asyncio.Lock()

async def get_instagram_service() -> InstagramService:
    """Retorna a instância global do serviço Instagram de forma thread-safe."""
    global _instance
    if _instance is None:
        async with _instance_lock:
            if _instance is None:
                _instance = InstagramService()
    return _instance 