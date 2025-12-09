document.addEventListener('DOMContentLoaded', () => {
    const todoInput = document.getElementById('todoInput');
    const addTodoBtn = document.getElementById('addTodoBtn');
    const todoList = document.getElementById('todoList');

    // Load todos from local storage
    let todos = JSON.parse(localStorage.getItem('todos')) || [];

    const saveTodos = () => {
        localStorage.setItem('todos', JSON.stringify(todos));
    };

    const renderTodos = () => {
        todoList.innerHTML = ''; // Clear current list
        todos.forEach((todo, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="${todo.completed ? 'completed' : ''}">${todo.text}</span>
                <button data-index="${index}">Delete</button>
            `;
            if (todo.completed) {
                li.classList.add('completed');
            }

            // Toggle completion
            li.querySelector('span').addEventListener('click', () => {
                todos[index].completed = !todos[index].completed;
                saveTodos();
                renderTodos();
            });

            // Delete todo
            li.querySelector('button').addEventListener('click', (e) => {
                const itemIndex = e.target.dataset.index;
                todos.splice(itemIndex, 1);
                saveTodos();
                renderTodos();
            });

            todoList.appendChild(li);
        });
    };

    const addTodo = () => {
        const todoText = todoInput.value.trim();
        if (todoText !== '') {
            todos.push({ text: todoText, completed: false });
            todoInput.value = '';
            saveTodos();
            renderTodos();
        }
    };

    addTodoBtn.addEventListener('click', addTodo);
    todoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTodo();
        }
    });

    renderTodos(); // Initial render
});

