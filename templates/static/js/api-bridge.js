// API Bridge - Connects frontend to MongoDB backend
const API_BASE = window.location.origin;

// Load data from backend on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE}/api/data`);
        const data = await response.json();
        
        if (data.users) {
            const systemData = {
                users: data.users,
                currentUser: null,
                functionalGroups: ['D&L', 'Administration', 'Training', 'Rajbhasha', 'Pension', 'Time Office', 'Leave', 'Bills', 'DAK']
            };
            localStorage.setItem('hr_system_final_v5', JSON.stringify(systemData));
        }
        
        if (data.tasks) {
            localStorage.setItem('hr_tasks_v5', JSON.stringify(data.tasks));
        }
        
        console.log('✅ Data loaded from MongoDB');
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
    }
});

// Sync to backend every 3 seconds
setInterval(async () => {
    try {
        const systemData = localStorage.getItem('hr_system_final_v5');
        const tasksData = localStorage.getItem('hr_tasks_v5');
        
        if (systemData && tasksData) {
            const system = JSON.parse(systemData);
            const tasks = JSON.parse(tasksData);
            
            await fetch(`${API_BASE}/api/data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ users: system.users, tasks: tasks })
            });
        }
    } catch (error) {
        console.error('Sync error:', error);
    }
}, 3000);

console.log('✅ MongoDB Backend Connected!');
