/**
 * @jest-environment jsdom
 */

const fs = require('fs');
const path = require('path');

const {
    taskList,
    importantTaskList,
    historyList,
    addTask,
    addImportantTask,
    toggleImportantTask,
    archiveCompleted
} = require('./todo');

describe('To-Do List App', () => {
    let script;
    let document;

    beforeEach(() => {
        // Load HTML
        const html = fs.readFileSync(path.resolve(__dirname, 'index.html'), 'utf8');
        document = window.document;
        document.body.innerHTML = html;

        // Clear localStorage
        localStorage.clear();

        // Load JS

        // Reset data
        taskList.length = 0;
        importantTaskList.length = 0;
        while (historyList.length) historyList.pop();
    });

    

    test('archiveCompleted should not throw when no completed tasks', () => {
        expect(() => archiveCompleted()).not.toThrow();
        expect(historyList.length).toBe(0);
    });

    

    test('addTask should not add empty task', () => {
        expect(addTask('')).toBe('empty');
        expect(taskList.length).toBe(0);
    });

    test('addImportantTask should not add empty task (bug: no alert)', () => {
        expect(addImportantTask('')).toBe('empty');
        expect(importantTaskList.length).toBe(0);
    });

    test('toggleImportantTask off-by-one bug', () => {
        addImportantTask('Test Important');
        // index=0, toggleImportantTask(0) actually accesses importantTaskList[-1]
        expect(() => toggleImportantTask(0)).toThrow();
    });

    
});