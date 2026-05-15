from models.user import User

class UserService:
    @staticmethod
    async def handle_add_point(user: User, point: int):
        return await user.add_point(point)