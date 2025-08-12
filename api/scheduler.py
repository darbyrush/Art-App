#!/usr/bin/env python3
"""
Scheduler for background tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from background_tasks import run_background_tasks

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manages scheduled background tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Run background tasks every 6 hours
        self.scheduler.add_job(
            run_background_tasks,
            trigger=IntervalTrigger(hours=6),
            id='background_tasks',
            name='Background Database Tasks',
            replace_existing=True
        )
        
        # Run cleanup daily at 2 AM
        self.scheduler.add_job(
            self._cleanup_job,
            trigger='cron',
            hour=2,
            minute=0,
            id='cleanup_job',
            name='Daily Database Cleanup',
            replace_existing=True
        )
    
    async def _cleanup_job(self):
        """Daily cleanup job"""
        try:
            from background_tasks import background_manager
            deleted_count = background_manager.cleanup_old_artworks()
            logger.info(f"Daily cleanup completed: {deleted_count} artworks deleted")
        except Exception as e:
            logger.error(f"Error in daily cleanup: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Background task scheduler started")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Background task scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_job_status(self):
        """Get status of all jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs

# Global scheduler instance
scheduler = TaskScheduler()

def start_background_scheduler():
    """Start the background task scheduler"""
    scheduler.start()

def stop_background_scheduler():
    """Stop the background task scheduler"""
    scheduler.stop() 