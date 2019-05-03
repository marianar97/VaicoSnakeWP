from celery.decorators import task

@task()
def print_hi():
    print('hi')

