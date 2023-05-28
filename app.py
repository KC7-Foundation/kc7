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
    print("""A Cybersecurity Game""")
    print("=============================")
    print("""Warning: Data will print to console as dataframe until you configure your ADX cluster.
See: https://github.com/kkneomis/kc7/wiki/Setting-up-you-Azure-Data-Explorer-cluster-in-the-Azure-Portal \n
If you care about the data but not the code: 
    See: https://github.com/kkneomis/kc7/wiki/No-code-Required!-Loading-the-test-KC7-cluster-into-your-free-Kusto-instance \n
For training Materials:
    See: https://github.com/kkneomis/kc7/blob/master/training_materials/KC7%20-%20Cyber%20Challenge%20Training.pdf
    """)

    print("""
To get started go to http://127.0.0.1:8889/login
Login username:password -> admin:admin 
    """)
    application.run(debug=True, port="8889")

