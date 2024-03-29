import os

from app import CustomError, ValidationError, ForbiddenError
from app import app, mail
from app.auth.services import Auth
from app.models import Users, Files
from app.serializers import UsersSchema, FilesSchema
from app.users.db import UserDBApi

users_schema = UsersSchema(many=True)
file_schema = FilesSchema()


# User service class
class UserService:
    def create(data: dict, current_user: Users, host: str, send_invitation_emails: bool = True) -> None:
        emails_to_invite = []
        email = data['email']
        if email:
            # Check if user already exists
            user = app.session.query(Users).filter_by(email=data['email']).first()
            if user:
                raise ValidationError({'message': 'Error when creating user to database: user already exists\n'})

            UserDBApi.create(data, current_user)
            emails_to_invite.append(email)

        if emails_to_invite and len(emails_to_invite):
            if not send_invitation_emails:
                return
        Auth.send_password_reset_email(email, host, 'invitation')

    def update(user_id: str, data: dict, current_user: Users):
        UserDBApi.update(user_id, data, current_user)

    def remove(user_id: str, current_user: Users):
        if str(current_user.id) == str(user_id):
            raise ValidationError({'message': 'Remove user error: Deleting himself\n'})
        if not current_user.role == 'admin':
            raise ValidationError({'message': 'Remove user error: Forbidden\n'})
        user = app.session.query(Users).filter_by(id=user_id).first()
        app.session.delete(user)
        app.session.commit()

    def get_all():
        users = app.session.query(Users)
        users = users.order_by(Users.email.asc()).all()
        users_dict = users_schema.dump(users)
        users_list = []
        for user_dict in users_dict:
            user = app.session.query(Users).filter_by(id=user_dict['id']).first()
            user_dict['avatars'] = []
            if len(user.avatar):
                for file_rel in user.avatar:
                    fileId = file_rel.id
                    file = app.session.query(Files).filter_by(id=fileId).first()
                    file_dict = file_schema.dump(file)
                    user_dict['avatars'].append(file_dict)
            users_list.append(user_dict)
        return users_list
