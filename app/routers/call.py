from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    prefix="/call",
    tags=['Calls']
)


### Create Call ###

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.CallResponse)
def create_call(call: schemas.CallCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.user_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"{current_user.username} is not allowed to create calls")

    if call.client_id == -1 and call.client_name == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Please provide client name or id!')

    # Get the client based on the provided client id or name

    if call.client_id != -1:
        client = db.query(models.Client).filter(
            models.Client.client_id == call.client_id).first()
    elif call.client_name != "":
        client = db.query(models.Client).filter(
            models.Client.client_name == call.client_name).first()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Client not found')

    # Update the call's client id and name if necessary
    if call.client_id == -1:
        call.client_id = client.client_id
    if call.client_name == "":
        call.client_name = client.client_name

    # Get the assigned user
    user = db.query(models.User).filter(models.User.user_id == call.assigned_to_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User not found')

    # Get the machine
    machine_1 = utils.get_machine_by_id_and_client_id(
        db, call.machine_id, call.client_id)
    if not machine_1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Machine not found')

    # Check if the machine belongs to the specified client
    machine_2 = utils.get_machine_by_id_and_client_id(
        db, call.machine_id, call.client_id)
    if not machine_2:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'Machine is not found at the specified client')

    if call.cause is None or call.cause == "":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Please specify the cause')

    # Create a new call
    new_call = models.Call(created_by=current_user.user_id,
                           client_id=call.client_id, assigned_to_id=call.assigned_to_id,
                           machine_id=call.machine_id, cause=call.cause)
    db.add(new_call)
    db.commit()
    db.refresh(new_call)
    return new_call

### Modify Calls ###


@router.put('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.CallResponse)
def update_call(
    updated_call: schemas.CallUpdate,
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if current_user.user_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Only admins can modify calls !')

    # Get the call
    call = db.query(models.Call).filter(models.Call.call_id == id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call with id {id} does not exist'
        )

    # Update the call based on the provided information
    if updated_call.client_id is not None and updated_call.client_id != call.client_id:
        # Client is changed, machine has to change too
        if updated_call.machine_id is None or updated_call.machine_id == call.machine_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Machine is not found at client {updated_call.client_id}. Machine needs to be changed."
            )

        machine = db.query(models.Machine).filter(
            models.Machine.machine_id == updated_call.machine_id,
            models.Machine.client_id == updated_call.client_id
        ).first()

        if not machine:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Machine is not found at the specified client."
            )

        call.client_id = updated_call.client_id
        call.machine_id = updated_call.machine_id

    if updated_call.machine_id is not None and updated_call.machine_id != call.machine_id:
        machine = db.query(models.Machine).filter(
            models.Machine.machine_id == updated_call.machine_id,
            models.Machine.client_id == call.client_id
        ).first()

        if not machine:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Machine is not found at the specified client."
            )

        call.machine_id = updated_call.machine_id

    if updated_call.assigned_to_id is not None and updated_call.assigned_to_id != call.assigned_to_id:
        user = db.query(models.User).filter(
            models.User.user_id == updated_call.assigned_to_id
        ).first()

        if not user or user != "engineer":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with id = {updated_call.assigned_to_id} does not exist or is not an Engineer.'
            )

        call.assigned_to_id = updated_call.assigned_to_id

    if updated_call.cause != "" and updated_call.cause != call.cause:
        call.cause = updated_call.cause

    db.commit()
    db.refresh(call)
    return call

### Get All Calls ###


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.CallResponse])
def get_calls(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    closed_search: Optional[bool] = None,
    search_assigned_to: Optional[int] = None,
    search_client: Optional[str] = None,
):
    query = db.query(models.Call)

    if current_user.user_type == "engineer":
        query = query.filter(models.Call.assigned_to_id ==
                             current_user.user_id)

    if search_assigned_to is not None:
        query = query.filter(models.Call.assigned_to_id == search_assigned_to)
    if search_client is not None:
        query = query.filter(models.Call.client_id == search_client)
    if closed_search is not None:
        query = query.filter(models.Call.closed == closed_search)

    calls = query.limit(limit).offset(skip).all()

    if not calls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')

    return calls

### Get one call ###


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.CallResponse)
def get_call(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    query = db.query(models.Call).filter(models.Call.call_id == id)

    if current_user.user_type == "admin":
        call = query.first()
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Not Found'
            )
        return call

    elif current_user.user_type == "engineer":
        query = query.filter(models.Call.assigned_to_id ==
                             current_user.user_id)
        call = query.first()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Call not found or does not belong to you'
            )
        return call

### Delete Call ###


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_call(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    if current_user.user_type == "engineer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Not Allowed'
        )

    call = db.query(models.Call).filter(models.Call.call_id == id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Call with id {id} does not exist'
        )

    db.delete(call)
    db.commit()

    return None


### Close Call ###

@router.put("/close/{id}", status_code=status.HTTP_200_OK, response_model=schemas.CallResponse)
def close_call(
    id: int,
    engineer_response : str,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    print(engineer_response)

    if current_user.user_type != "engineer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Engineers are allowed to close their calls"
        )

    call = db.query(models.Call).filter(
        models.Call.call_id == id, models.Call.assigned_to_id == current_user.user_id
    ).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are only allowed to close your calls"
        )

    if call.closed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Call already closed!"
        )
    
    if engineer_response is None :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Provide a response first !")

    call.closed = True
    call.engineer_response = engineer_response
    db.commit()
    return call
