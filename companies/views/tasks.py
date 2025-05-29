from companies.views.base import Base
from companies.utils.permissions import TaskPermission
from companies.serializers import TaskSerializer, TasksSerializer
from companies.models import Task

from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
import datetime




class Tasks(Base):
    permission_classes = [TaskPermission]

    def get(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)

        tasks = Task.objects.filter(enterprise_id=enterprise_id).all()

        serializer = TasksSerializer(tasks, many=True)

        return Response({"tasks": serializer.data})   
    

    def post(self, request):
        # Obtendo e validando os dados
        employee_id = request.data.get("employee_id")
        title = request.data.get("title", "").strip()
        description = request.data.get("description", "").strip()
        status_id = request.data.get("status_id")
        due_date = request.data.get("due_date")

        if not employee_id or not title or not status_id:
            return Response(
                {"error": "Os campos 'employee_id', 'title' e 'status_id' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(title) > 125:
            return Response(
                {"error": "O título da tarefa deve ter no máximo 125 caracteres."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtendo funcionário e status
        employee = self.get_employee(employee_id, request.user.id)
        _status = self.get_status(status_id)

        # Validar formato da data, se fornecida
        if due_date:
            try:
                due_date = datetime.datetime.strptime(due_date, "%d/%m/%Y %H:%M")
            except ValueError:
                return Response(
                    {"error": "Formato da data inválido. Use: d/m/Y H:M"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Criando a tarefa
        task = Task.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            employee_id=employee_id,
            enterprise_id=employee.enterprise.id,
            status_id=status_id
        )

        serializer = TaskSerializer(task)

        return Response({"task": serializer.data}, status=status.HTTP_201_CREATED)

class TaskDetail(Base):
    permission_classes = [TaskPermission]

    def get(self, request, task_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        task = self.get_task(task_id, enterprise_id)

        serializer = TaskSerializer(task)

        return Response({"task": serializer.data})


    

    def put(self, request, task_id):
        # Obtendo a empresa associada ao usuário
        enterprise_id = self.get_enterprise_id(request.user.id)
        task = self.get_task(task_id, enterprise_id)

        # Obtendo e validando os dados
        title = request.data.get("title", "").strip() or task.title
        employee_id = request.data.get("employee_id", task.employee.id)
        description = request.data.get("description", "").strip() or task.description
        status_id = request.data.get("status_id", task.status.id)
        due_date = request.data.get("due_date", task.due_date)

        # Validar status e funcionário
        self.get_status(status_id)
        self.get_employee(employee_id, request.user.id)

        # Validar formato da data se houver alteração
        if due_date and due_date != task.due_date:
            try:
                due_date = datetime.datetime.strptime(due_date, "%d/%m/%Y %H:%M")
            except ValueError:
                return Response(
                    {"error": "Formato da data inválido. Use: d/m/Y H:M"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Criando dados para atualização
        data = {
            "title": title,
            "description": description,
            "due_date": due_date
        }

        serializer = TaskSerializer(task, data=data, partial=True)

        if not serializer.is_valid():
            return Response({"error": "Não foi possível editar a tarefa"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.update(task, serializer.validated_data)

        # Atualizando os campos diretamente no objeto
        task.status_id = status_id
        task.employee_id = employee_id
        task.save()

        return Response({"task": serializer.data}, status=status.HTTP_200_OK)


    def delete(self, request, task_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        task = self.get_task(task_id, enterprise_id).delete()

        return Response({"success": True})