""" 
Created on : 24/08/23 8:39 am
@author : ds  
"""

import logging
from typing import List

import fastapi
from fastapi import Query, HTTPException

from app.utils.helper import (
    load_list,
    save_list,
    generate_id,
    get_todo_details,
    remove_todo,
    update_todo,
)
from app.utils.config_manager import config_manager
from app.data.models import TodoItem, ReturnTodo, UpdateTodo

router = fastapi.APIRouter()
config_manager.configure_logging()

@router.get("/")
async def read_root():
    """root route"""
    logging.info("Request received at root route.")
    return {"message": "Welcome to API Challenge"}


@router.get("/todos", response_model=List[ReturnTodo])
async def read_todos(
    page: int = Query(default=1, description="Page Number"),
    per_page: int = Query(default=5, description="Items per page"),
):
    """Get list of to-do items"""
    logging.debug(f"Fetching app for page {page}, per_page {per_page}")
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=400, detail="Page and per_page must be positive integer."
        )

    skip = (page - 1) * per_page
    todos = load_list()[skip : skip + per_page]

    logging.debug(f"Returning {len(todos)} app")

    return todos


@router.post("/todos")
async def add_todo(todo: TodoItem):
    """This is post route to add a To-do item"""
    try:
        logging.debug("Adding a new todo item")

        todo = todo.model_dump()
        todo.update(id=generate_id())
        data = load_list()
        data.append(todo)
        save_list(data)

        logging.debug(f"Added todo item with ID: {todo['id']}")

        return todo
    except Exception as e:
        error_message = f"Internal Server Error: {e}"
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@router.get("/todos/{todo_id}")
async def read_todo(todo_id):
    """return todo details for a given id"""
    result = get_todo_details(todo_id)
    logging.info(f"Retrieved details for given id {todo_id} ")
    return result


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id):
    """Delete an item"""
    logging.debug(f"Deleting item with ID: {todo_id}")
    result = remove_todo(todo_id)
    return result


@router.put("/todos/{todo_id}")
async def update_todo_list(todo: UpdateTodo, todo_id):
    """Update an item"""
    logging.debug(f"Updating item with ID: {todo_id}")

    todo = todo.model_dump()
    result = update_todo(todo_id, todo)

    if "error" in result:
        error_message = result["error"]
        logging.error(f"Error while updating todo: {error_message}")

    return result
