from companies.views.base import Base
from companies.utils.permissions import EmployeesPermission, GroupsPermission
from companies.models import Employee, Enterprise
from companies.serializers import EmployeeSerializer, EmployeesSerializer

from accounts.auth import Authentication
from accounts.models import User, User_Groups
from rest_framework import status

from rest_framework.views import Response, status
from rest_framework.exceptions import APIException


class Employees(Base):
    permission_classes = [EmployeesPermission]

    def get(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)

        # Get owner of enterprise
        owner_id = Enterprise.objects.values('user_id').filter(id=enterprise_id).first()['user_id']

        employees = Employee.objects.filter(enterprise_id=enterprise_id).exclude(user_id=owner_id).all()

        serializer = EmployeesSerializer(employees, many=True)

        return Response({"employees": serializer.data})
    
   

def post(self, request):
    # Obtendo e validando os dados da requisição
    name = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')

    if not name or not email or not password:
        return Response({"error": "Nome, email e senha são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        enterprise_id = self.get_enterprise_id(request.user.id)
        signup_user = Authentication.signup(
            self,
            name=name,
            email=email,
            password=password,
            type_account='employee',
            company_id=enterprise_id
        )
    except APIException as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(signup_user, User):
        return Response({"error": "Erro ao criar usuário"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"success": True}, status=status.HTTP_201_CREATED)


class EmployeeDetail(Base):
    permission_classes = [EmployeesPermission]

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id, request.user.id)

        serializer = EmployeeSerializer(employee)

        return Response(serializer.data)
   

    def put(self, request, employee_id):
        # Obtendo e validando os dados
        groups = request.data.get("groups", "")
        name = request.data.get("name", "").strip()
        email = request.data.get("email", "").strip()

        # Obtendo o funcionário e validando sua existência
        employee = self.get_employee(employee_id, request.user.id)

        # Se o email for diferente e já existir, retorna erro
        if email and email != employee.user.email and User.objects.filter(email=email).exists():
            return Response({"error": "Esse email já está em uso"}, status=status.HTTP_400_BAD_REQUEST)

        # Atualizando o usuário
        User.objects.filter(id=employee.user.id).update(
            name=name or employee.user.name,
            email=email or employee.user.email
        )

        # Atualizando os grupos
        User_Groups.objects.filter(user_id=employee.user.id).delete()

        if groups:
            try:
                group_ids = [int(group_id) for group_id in groups.split(",")]
                for group_id in group_ids:
                    self.get_group(group_id, employee.enterprise.id)
                    User_Groups.objects.create(
                        group_id=group_id,
                        user_id=employee.user.id
                    )
            except ValueError:
                return Response({"error": "IDs de grupo inválidos"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": True}, status=status.HTTP_200_OK)

    def delete(self, request, employee_id):
        employee = self.get_employee(employee_id, request.user.id)

        check_if_owner = User.objects.filter(id=employee.user.id, is_owner=1).exists()

        if check_if_owner:
            raise APIException('Você não pode demitir o dono da empresa')
        
        employee.delete()
        
        User.objects.filter(id=employee.user.id).delete()

        return Response({"success": True})