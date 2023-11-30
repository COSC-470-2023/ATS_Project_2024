#### We are testing in the Yuan's local environment ##### 
import connect
import traceback
from sqlalchemy import text 

def dataDeletion(table, conn):
    #Delete entries that is stored longer than 3 years
    conn.execute(text(f"DELETE FROM {table} WHERE date < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)"))
    
def main():
    try:
        #create with context manager, conn is created only for this script, commit the conn will not affect others
        with connect.connect() as conn:
            result = (conn.execute(text(f"SHOW TABLES"))).fetchall()
            #Iterate through all the tables in the database and fetch the table name for delete operation
            #Need to modify so that we DO NOT DELETE any data in the change_log file!!!!
            for tables in result:
                table = tables[0] 
                if table != 'company_changelogs':
                    dataDeletion(table, conn)
                    conn.commit()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

# protected entrypoint
if __name__ == "__main__":
    main()