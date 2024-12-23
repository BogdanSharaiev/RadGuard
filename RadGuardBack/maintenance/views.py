import os
from datetime import datetime
import psycopg2
from django.conf import settings
from django.core.management import call_command
from myapi.permissions import IsAdminUserPermission
from psycopg2 import sql
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class PostgresDBManagementView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserPermission]

    def post(self, request, action):
        if action == 'migrate':
            return self.perform_migrations()
        elif action == 'backup':
            return self.create_backup()
        else:
            return Response({'error': f'Error action: {action}. Use "migrate" or "backup".'}, status=400)

    def perform_migrations(self):
        try:
            call_command('makemigrations')
            call_command('migrate')
            return Response({'message': 'Migrate succesful.'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def create_backup(self):
        try:
            backup_dir = 'C:/backups'
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')

            db_settings = settings.DATABASES['default']
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_host = db_settings.get('HOST', 'localhost')
            db_port = db_settings.get('PORT', '5432')
            db_password = db_settings['PASSWORD']

            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.autocommit = True

            cursor = conn.cursor()

            with open(backup_file, 'w') as f:
                f.write(f'-- Backup of {db_name} database\n')
                f.write(f'-- Created on {timestamp}\n\n')

                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    f.write(f'-- Dumping data for table: {table_name}\n')

                    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
                    rows = cursor.fetchall()

                    for row in rows:
                        insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(map(str, row))});\n"
                        f.write(insert_sql)

                    f.write(f'-- End of dump for table: {table_name}\n\n')

            cursor.close()
            conn.close()

            return Response({
                'message': 'Backup successful.',
                'backup_file': backup_file
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

