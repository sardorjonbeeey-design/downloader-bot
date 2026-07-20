"""
Admin handlers - Analytics and Stats
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

ADMIN_IDS = [123456789]  # Replace with your Telegram user ID

class StatsManager:
    def __init__(self):
        self.stats_file = Path('data/stats.json')
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats = self.load_stats()
    
    def load_stats(self):
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {
            'total_downloads': 0,
            'downloads_by_platform': {},
            'downloads_by_user': {},
            'daily_downloads': {},
            'start_date': datetime.now().isoformat()
        }
    
    def save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def add_download(self, user_id: int, platform: str):
        self.stats['total_downloads'] += 1
        
        if platform not in self.stats['downloads_by_platform']:
            self.stats['downloads_by_platform'][platform] = 0
        self.stats['downloads_by_platform'][platform] += 1
        
        user_id_str = str(user_id)
        if user_id_str not in self.stats['downloads_by_user']:
            self.stats['downloads_by_user'][user_id_str] = 0
        self.stats['downloads_by_user'][user_id_str] += 1
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_downloads']:
            self.stats['daily_downloads'][today] = 0
        self.stats['daily_downloads'][today] += 1
        
        self.save_stats()
    
    def get_stats(self):
        return self.stats

stats_manager = StatsManager()

async def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    return user_id in ADMIN_IDS

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("⛔ This command is for admin only.")
        return
    
    stats = stats_manager.get_stats()
    
    platform_lines = []
    for platform, count in stats['downloads_by_platform'].items():
        platform_lines.append(f"  {platform}: {count}")
    
    top_users = sorted(
        stats['downloads_by_user'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    user_lines = []
    for user_id, count in top_users:
        user_lines.append(f"  {user_id}: {count}")
    
    stats_text = (
        "📊 *Yukla Pro Stats*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 Total downloads: {stats['total_downloads']}\n\n"
        "*By platform:*\n" + "\n".join(platform_lines) + "\n\n"
        "*Top users:*\n" + "\n".join(user_lines) + "\n\n"
        f"📅 Started: {stats['start_date'][:10]}\n"
        f"📈 Today: {stats['daily_downloads'].get(dat