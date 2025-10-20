// Arrays for tasks
let taskList = [];
let importantTaskList = [];
let historyList = []; // 修正为局部变量

function addTask(task) {
    if (task.trim() === '') {
        return 'empty';
    }
    taskList.push({ text: task, completed: false });
    return 'added';
}

function addImportantTask(task) {
    if (task.trim() === '') {
        return 'empty';
    }
    importantTaskList.push({ text: task, completed: false });
    return 'added';
}

function toggleImportantTask(index) {
    // BUG: Off-by-one error, mistakenly uses index - 1
    importantTaskList[index - 1].completed = !importantTaskList[index - 1].completed;
}

function archiveCompleted() {
    const completedTasks = taskList.filter(task => task.completed);
    historyList = historyList.concat(completedTasks);
    taskList = taskList.filter(task => !task.completed);
}

module.exports = {
    taskList,
    importantTaskList,
    historyList,
    addTask,
    addImportantTask,
    toggleImportantTask,
    archiveCompleted
};