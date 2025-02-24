def create_user_for_test(client):
    user_data = {
        "full_name": "John Doe",
        "user_name": "johndoe123",
        "email": "john.doe@example.com",
        "password": "StrongPassword123!",
        "phoneNumber": "+92 1234567890",
        "address": "123 Main Street, Springfield",
        "roleStatus": "active",
        "activeRole": "customer",
        "roles": [
            {
                "role_id": 1
            }
        ]
    }

    response = client.post("/user/register/user", json=user_data)
    return response