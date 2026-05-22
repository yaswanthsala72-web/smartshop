"""
Management command to automatically advance order statuses every 10 minutes.
Stages: Pending -> Confirmed -> Packed -> Shipped -> Out for Delivery -> Delivered

Usage:
    python manage.py auto_advance_orders
"""

import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Order


class Command(BaseCommand):
    help = 'Automatically advances order statuses every 10 minutes'

    STAGES = [
        'Pending',
        'Confirmed',
        'Packed',
        'Shipped',
        'Out for Delivery',
        'Delivered',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=600,  # 10 minutes in seconds
            help='Interval in seconds between status advances (default: 600 = 10 min)',
        )

    def get_next_status(self, current_status):
        """Return the next status in the pipeline, or None if already Delivered."""
        try:
            idx = self.STAGES.index(current_status)
            if idx < len(self.STAGES) - 1:
                return self.STAGES[idx + 1]
        except ValueError:
            pass
        return None

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(self.style.SUCCESS(
            '\n>> Auto Order Advancement started!'
            '\n   Interval: {} seconds ({} minutes)'
            '\n   Press Ctrl+C to stop.\n'.format(interval, interval // 60)
        ))

        try:
            while True:
                # Get all orders that are NOT yet delivered
                active_orders = Order.objects.exclude(status='Delivered')

                if not active_orders.exists():
                    self.stdout.write(self.style.WARNING(
                        '[{}] No active orders to advance.'.format(
                            timezone.now().strftime("%H:%M:%S")
                        )
                    ))
                else:
                    for order in active_orders:
                        old_status = order.status
                        new_status = self.get_next_status(old_status)

                        if new_status:
                            order.status = new_status

                            # Auto-update payment status when confirmed
                            if new_status == 'Confirmed' and order.payment_status == 'Pending':
                                order.payment_status = 'Paid'
                                self.stdout.write(self.style.SUCCESS(
                                    '   [PAYMENT] Order #{} payment status -> Paid'.format(order.id)
                                ))

                            order.save()
                            self.stdout.write(self.style.SUCCESS(
                                '[{}] Order #{}: {} -> {}'.format(
                                    timezone.now().strftime("%H:%M:%S"),
                                    order.id, old_status, new_status
                                )
                            ))
                        else:
                            self.stdout.write(
                                '[{}] Order #{}: Already at final stage.'.format(
                                    timezone.now().strftime("%H:%M:%S"),
                                    order.id
                                )
                            )

                self.stdout.write(
                    '   >> Next advancement in {} minutes...\n'.format(interval // 60)
                )
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nAuto advancement stopped.'))
