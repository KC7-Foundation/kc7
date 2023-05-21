from app import application

if __name__ == '__main__':
    print("""
                                            
    _/    _/        _/_/_/     _/_/_/_/_/   
   _/  _/        _/                   _/    
  _/_/          _/                 _/       
 _/  _/        _/               _/          
_/    _/        _/_/_/       _/             
                                            
    """)
    print("=============================")
    print("""A Cybersecurity Game - by the KC7 Foundation""")
    print("=============================")
    print("""Warning: In debug mode, data will print to the testlogs folder. Look there for the text version of the logs. 
See: https://github.com/kkneomis/kc7/wiki/Setting-up-you-Azure-Data-Explorer-cluster-in-the-Azure-Portal \n
If you care about the data but not the code: 
    See: kc7cyber.com/modules and kc7cyber.com/demo  \n
    """)

    print("""
To get started go to http://127.0.0.1:8889/
    """)
    application.run(debug=True, port="8889")

