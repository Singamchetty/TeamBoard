from django.core.management.base import BaseCommand

from api.models import KBEntry

KB_ENTRIES = [
    ('What is select_related in Django ORM?',
     'select_related performs a SQL JOIN and fetches related objects in a single query, '
     'reducing the number of database hits for foreign key and one-to-one relationships.',
     KBEntry.Category.DATABASE),
    ('What is prefetch_related used for?',
     'prefetch_related performs a separate query per relationship and joins the results in '
     'Python, which is efficient for many-to-many and reverse foreign key relationships.',
     KBEntry.Category.DATABASE),
    ('How does transaction.atomic() work?',
     'transaction.atomic() wraps a block of code in a database transaction. If an exception '
     'is raised inside the block, all changes are rolled back, ensuring atomicity.',
     KBEntry.Category.DATABASE),
    ('What is a JWT token?',
     'A JWT (JSON Web Token) is a compact, signed token used to authenticate requests. It '
     'contains claims about the user and is verified using a secret key.',
     KBEntry.Category.API),
    ('When should I use Q objects?',
     'Q objects let you build complex queries with OR, AND, and NOT logic that cannot be '
     'expressed with simple keyword filtering alone, e.g. Q(a=1) | Q(b=2).',
     KBEntry.Category.DATABASE),
    ('What is the difference between authentication and authorization?',
     'Authentication verifies who a user is (e.g. via credentials or a token), while '
     'authorization determines what an authenticated user is allowed to do.',
     KBEntry.Category.API),
    ('How do Django signals work?',
     'Signals allow decoupled applications to get notified when certain actions occur '
     'elsewhere, such as post_save firing after a model instance is saved.',
     KBEntry.Category.FRAMEWORK),
    ('What is horizontal scaling in cloud infrastructure?',
     'Horizontal scaling adds more machines to handle load, as opposed to vertical scaling '
     'which adds more resources (CPU/RAM) to a single machine.',
     KBEntry.Category.CLOUD),
    ('What is a load balancer?',
     'A load balancer distributes incoming network traffic across multiple servers to '
     'ensure no single server becomes overwhelmed, improving availability and reliability.',
     KBEntry.Category.CLOUD),
    ('What is REST API statelessness?',
     'Statelessness means each request from a client must contain all the information '
     'needed to process it; the server does not store client session state between requests.',
     KBEntry.Category.API),
    ('What is database indexing?',
     'An index is a data structure that improves the speed of data retrieval on a table at '
     'the cost of additional writes and storage space.',
     KBEntry.Category.DATABASE),
    ('What is middleware in Django?',
     'Middleware is a framework of hooks into Django\'s request/response processing, used '
     'for cross-cutting concerns like authentication, sessions, and security headers.',
     KBEntry.Category.FRAMEWORK),
]


class Command(BaseCommand):
    help = 'Seed the knowledge base with sample Q&A entries.'

    def handle(self, *args, **options):
        created_count = 0
        for question, answer, category in KB_ENTRIES:
            _, created = KBEntry.objects.get_or_create(
                question=question,
                defaults={'answer': answer, 'category': category},
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {created_count} new KB entries ({len(KB_ENTRIES)} total defined).'
            )
        )
