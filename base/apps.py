from django.apps import AppConfig
from django.db import connection, IntegrityError
from django.db.models.query import QuerySet


class BaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'base'

        
        
    def ready(self):
            if connection.vendor in ["microsoft", "mssql"]:
                original_bulk_create = QuerySet.bulk_create

                def safe_bulk_create(queryset_self, objs, *args, **kwargs):
                    if kwargs.get("ignore_conflicts"):
                    # 1. Remove the unsupported flag so Django stops throwing NotSupportedError
                        kwargs.pop("ignore_conflicts", None)
                    
                    # 2. Try standard bulk creation
                        try:
                            return original_bulk_create(queryset_self, objs, *args, **kwargs)
                        except IntegrityError:
                        # 3. Fallback: Save items one by one, skipping duplicate key conflicts safely
                            created_objects = []
                            for obj in objs:
                                try:
                                    obj.save()
                                    created_objects.append(obj)
                                except IntegrityError:
                                    pass # Conflict safely ignored on MSSQL
                            return created_objects

                    return original_bulk_create(queryset_self, objs, *args, **kwargs)

            # Apply the patch directly to Django's base QuerySet class
            QuerySet.bulk_create = safe_bulk_create