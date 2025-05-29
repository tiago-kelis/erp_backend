from companies.views.base import Base
from companies.utils.exceptions import RequiredFields
from companies.utils.permissions import GroupsPermission
from companies.serializers import GroupsSerializer

from accounts.models import Group, Group_Permissions

from rest_framework.views import Response
from rest_framework.exceptions import APIException
from rest_framework import status

from django.contrib.auth.models import Permission


class Groups(Base):
    permission_classes = [GroupsPermission]

    def get(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)
        groups = Group.objects.filter(enterprise_id=enterprise_id).all()

        serializer = GroupsSerializer(groups, many=True)

        return Response({"groups": serializer.data})


    def post(self, request):
        # Obtendo e validando os dados
        enterprise_id = self.get_enterprise_id(request.user.id)
        name = request.data.get("name", "").strip()
        permissions = request.data.get("permissions", "")

        if not name:
            return Response({"error": "O nome do grupo é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            created_group = Group.objects.create(name=name, enterprise_id=enterprise_id)
        except Exception:
            return Response({"error": "Erro ao criar grupo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if permissions:
            try:
                permission_ids = [int(item) for item in permissions.split(",")]

                for item in permission_ids:
                    if not Permission.objects.filter(id=item).exists():
                        created_group.delete()
                        return Response(
                            {"error": f"A permissão {item} não existe"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if not Group_Permissions.objects.filter(group_id=created_group.id, permission_id=item).exists():
                        Group_Permissions.objects.create(group_id=created_group.id, permission_id=item)

            except ValueError:
                created_group.delete()
                return Response(
                    {"error": "Envie as permissões no formato correto (exemplo: 1,2,3,4)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class GroupDetail(Base):
    permission_classes = [GroupsPermission]

    def get(self, request, group_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        self.get_group(group_id, enterprise_id)
        group = Group.objects.filter(id=group_id).first()

        serializer = GroupsSerializer(group)

        return Response({"group": serializer.data})


    def put(self, request, group_id):
        # Obtendo e validando os dados
        enterprise_id = self.get_enterprise_id(request.user.id)
        self.get_group(group_id, enterprise_id)  # Confirma se o grupo existe antes de modificar

        name = request.data.get("name", "").strip()
        permissions = request.data.get("permissions", "")

        # Atualizar nome do grupo, se fornecido
        if name:
            Group.objects.filter(id=group_id).update(name=name)

        # Deletar permissões antigas antes de adicionar as novas
        Group_Permissions.objects.filter(group_id=group_id).delete()

        if permissions:
            try:
                permission_ids = [int(item) for item in permissions.split(",")]

                for item in permission_ids:
                    if not Permission.objects.filter(id=item).exists():
                        return Response(
                            {"error": f"A permissão {item} não existe"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if not Group_Permissions.objects.filter(group_id=group_id, permission_id=item).exists():
                        Group_Permissions.objects.create(group_id=group_id, permission_id=item)

            except ValueError:
                return Response(
                    {"error": "Envie as permissões no formato correto (exemplo: 1,2,3,4)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({"success": True}, status=status.HTTP_200_OK)
        
    def delete(self, request, group_id):
        enterprise_id = self.get_enterprise_id(request.user.id)

        Group.objects.filter(id=group_id, enterprise_id=enterprise_id).delete()

        return Response({"success": True})