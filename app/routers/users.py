from fastapi import (
    APIRouter,
    Path,
    Depends
)

from app.dependencies import (
    get_user_id
)

from app.models.forms import (
    CreateAccountForm,
    LoginForm,
    UpdateProfileForm
)

from app.models.responses import (
    Response,
    AuthResponse,
    BalanceResponse,
    DashboardResponse,
)


from app.controllers.users import (
    create_user,
    authenticate_user,
    update_profile,
    probe_username
)

from app.controllers.transactions import (
    get_dashboard_data,
    get_balance
)


router = APIRouter(prefix='/api/users', tags=['Users'])


@router.post("/register", response_model=Response)
def create_user_route(data: CreateAccountForm):

    data = data.model_dump()
    user = create_user(data)

    return Response.cook(message="User Created successfully!")


@router.post("/login", response_model=AuthResponse)
def login_route(data: LoginForm):

    data = data.model_dump()
    token: str = authenticate_user(**data)

    return AuthResponse.cook(data={'token': token})


@router.put("/update", response_model=Response)
def update_profile_route(
    data: UpdateProfileForm,
    user_id: int = Depends(get_user_id)
):

    data = data.model_dump(exclude_none=True)
    update_profile(user_id, data)

    return Response.cook()


@router.get("/balance", response_model=BalanceResponse)
def get_balance_route(user_id: int = Depends(get_user_id)):

    balance: int = get_balance(user_id)
    return BalanceResponse.cook(data={'balance': balance})


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_route(user_id: int = Depends(get_user_id)):

    dashboard_data = get_dashboard_data(user_id)
    return DashboardResponse.cook(data=dashboard_data)


@router.get("/{username}", response_model=Response)
def probe_username_route(username: str = Path):

    return Response.cook(
        data={'user_id': probe_username(username)}
    )

