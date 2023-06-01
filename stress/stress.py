import json
import threading

from app.app import create_app as app


class Stress:

    def __init__(self, auto:bool=True) -> None:
        self.auto = auto

    def create_credentials(self, pos:int) -> tuple[str, str, bool]:

        #usernames = [f'user_{str(i)}' for i in range(1, (10 * incremental) + 1)]
        #passwords = ['password' for  _ in range(1, (10 * incremental) + 1)]
        #is_admin = [False for  _ in range(1, (10 * incremental) + 1)]

        username = f'user_{pos}'
        password = 'password'
        is_admin = False

        return username, password, is_admin
    
    def threaded_create_users(self, username:str, password:str, is_admin:bool) -> bool:
        
        with app().test_client() as client:
            
            headers = { 'Authorization': f'Basic admin:admin', 'Content-Type': 'application/json' }
            
            try:

                res = client.post('/api/create/user', data=json.dumps({'users': [username, password, is_admin]}), headers=headers)
                if res.json is not None:
                    return False
                return True
            
            except:

                return False
        
    def prepare_users(self, incremental:int) -> list[threading.Thread]:
        
        list_threads:list[threading.Thread] = []

        with app().app_context() as app:
            #app
            pass

        for pos in range(1, (10 * incremental) +1):
            list_threads.append(threading.Thread(target=self.threaded_create_users, args=self.create_credentials(pos=pos)))
        
        return list_threads

    def create_users(self, max_iter:int=10):

        for i in range(1, max_iter + 1):
            
            list_threads:list[threading.Thread] = self.prepare_users(incremental=i)
            for t in list_threads:
                t.start()
            
            for t in list_threads:
                t.join()


            
        

    
    

            
