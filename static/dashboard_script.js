document.addEventListener('DOMContentLoaded', () => {
    // Set today's date in input
    document.getElementById('date').valueAsDate = new Date();
    
    fetchData();

    const budgetForm = document.getElementById('budgetForm');
    if(budgetForm) {
        budgetForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const amount = document.getElementById('monthlyBudget').value;
            
            const res = await fetch('/api/budget', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ amount: amount })
            });

            if(res.ok) {
                alert("Budget Set!");
                fetchData(); // Refresh UI
            }
        });
    }

    // Handle Form Submit
    document.getElementById('expenseForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const expenseData = {
            date: document.getElementById('date').value,
            category: document.getElementById('category').value,
            amount: document.getElementById('amount').value,
            description: document.getElementById('description').value
        };

        const res = await fetch('/api/expenses', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(expenseData)
        });
        
        const data = await res.json();
        if(data.status === 'success') {
            alert("Expense Added!");
            fetchData(); // Refresh data
            e.target.reset(); // Clear form
            document.getElementById('date').valueAsDate = new Date();
        }
    });
});

async function fetchData() {
    const res = await fetch('/api/expenses');
    const data = await res.json();
    
    // 1. Update Total Spend
    if(document.getElementById('totalSpend')) {
        document.getElementById('totalSpend').textContent = `₹${data.total_spend}`;
    }
    if(document.getElementById('displayBudget')) {
        document.getElementById('displayBudget').textContent = `₹${data.budget}`;
        document.getElementById('displaySpent').textContent = `₹${data.total_spend}`;
        document.getElementById('displayRemaining').textContent = `₹${data.remaining}`;
    }

    // 2. Update Transaction List
    const list = document.getElementById('transactionList');
    if(list) {
        list.innerHTML = '';
        if(data.expenses.length === 0) {
            list.innerHTML = '<li class="empty-state">No transactions yet.</li>';
        } else {
            data.expenses.forEach(exp => {
                const li = document.createElement('li');
                li.className = 'transaction-item';
                li.innerHTML = `
                    <div class="t-info">
                        <div class="t-icon"><i class="fa-solid fa-receipt"></i></div>
                        <div>
                            <div>${exp.category}</div>
                            <small style="color:#94a3b8">${exp.date}</small>
                        </div>
                    </div>
                    <div class="t-amount">- ₹${exp.amount}</div>
                `;
                list.appendChild(li);
            });
        }
    }

    // 4. Update Chart
    if(document.getElementById('expenseChart')) {
        renderChart(data.chart_data);
    }
}

let myChart = null;
function renderChart(data) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    if(myChart) myChart.destroy(); // Destroy old chart before creating new one

    const labels = data.map(item => item.category);
    const values = data.map(item => item.total);

    myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { usePointStyle: true } }
            }
        }
    });
}