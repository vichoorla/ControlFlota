from django.db.backends.mysql.base import DatabaseWrapper

def patch_mariadb_check():
    original_check = DatabaseWrapper.check_database_version_supported
    
    def new_check(self):
        try:
            original_check(self)
        except Exception as e:
            if "MariaDB 10.5" in str(e):
                print("Advertencia: MariaDB 10.4 detectado, continuando...")
                return
            raise e
    
    DatabaseWrapper.check_database_version_supported = new_check

patch_mariadb_check()