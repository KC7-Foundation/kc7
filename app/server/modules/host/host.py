from app import db
from app.server.modules.organization.Company import Company

class Host(db.Model):
    """
    A class to model a host/machine
    """

    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    host_type = db.Column(db.String(50))

    def __init__(self, name: str, host_type: str) -> None:
        self.name = name
        self.host_type = host_type

    def __repr__(self) -> str:
        return '<Host %r>' % self.name


class Endpoint(Host):
    """
    A class to model a endpoint 
    Endpoints are devices like laptops and desktop used by individual users
    From simplification, we have a 1-1 relationship for User <-> Endpoint
    """

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    def __init__(self, name: str) -> None:
        super().__init__(name, host_type="endpoint")


class Server(Host):
    """
    A class to model a server 
    Servers are not directly associated with any one user
    Servers can be of multiple types including
    - Exchange, SSH, VPN, File, Web
    """
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    # company = db.relationship('Company', backref=db.backref('servers', lazy='dynamic'))

    def __init__(self, name: str, server_type: str) -> None:
        super().__init__(name, host_type="server")

        self.server_type = server_type


