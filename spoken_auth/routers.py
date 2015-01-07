class DrupalAuthRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'spoken_auth':
            return 'spoken'
        if model._meta.app_label == 'migrate_spoken':
            return 'cdeep'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'spoken_auth':
            return 'spoken'
        if model._meta.app_label == 'migrate_spoken':
            return 'cdeep'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        return True
