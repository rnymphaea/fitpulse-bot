import io
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from typing import Dict, List

async def generate_nutrition_chart(meals_data: List[Dict]) -> io.BytesIO:
    sorted_meals = sorted(meals_data, key=lambda x: datetime.strptime(x['time'], '%H:%M'))
    
    times = []
    cumulative_proteins = []
    cumulative_fats = []
    cumulative_carbs = []
    cumulative_fiber = []
    
    total_protein = 0
    total_fat = 0
    total_carb = 0
    total_fiber = 0
    
    for meal in sorted_meals:
        meal_protein = 0
        meal_fat = 0
        meal_carb = 0
        meal_fiber = 0
        
        for product in meal['products']:
            meal_protein += product['protein'] * product['quantity'] / 1000
            meal_fat += product['fats'] * product['quantity'] / 1000
            meal_carb += product['carbs'] * product['quantity'] / 1000
            meal_fiber += product['fiber'] * product['quantity'] / 1000
        
        total_protein += meal_protein
        total_fat += meal_fat
        total_carb += meal_carb
        total_fiber += meal_fiber
        
        times.append(meal['time'])
        cumulative_proteins.append(total_protein)
        cumulative_fats.append(total_fat)
        cumulative_carbs.append(total_carb)
        cumulative_fiber.append(total_fiber)
    
    fig = plt.figure(figsize=(14, 10), facecolor='#f5f5f5')
    plt.subplots_adjust(hspace=0.4)
    
    ax1 = plt.subplot2grid((2, 1), (0, 0))
    
    colors = {
        'Белки': '#2196F3',
        'Жиры': '#FF9800',
        'Углеводы': '#9C27B0',
        'Клетчатка': '#4CAF50'
    }
    
    ax1.plot(times, cumulative_proteins, label='Белки', marker='o', color=colors['Белки'], linewidth=2.5)
    ax1.plot(times, cumulative_fats, label='Жиры', marker='o', color=colors['Жиры'], linewidth=2.5)
    ax1.plot(times, cumulative_carbs, label='Углеводы', marker='o', color=colors['Углеводы'], linewidth=2.5)
    ax1.plot(times, cumulative_fiber, label='Клетчатка', marker='o', color=colors['Клетчатка'], linewidth=2.5)
    
    ax1.set_title('Динамика потребления нутриентов', fontsize=16, pad=20)
    ax1.set_ylabel('Граммы', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_facecolor('#ffffff')
    
    for i, (p, f, c, fb) in enumerate(zip(cumulative_proteins, cumulative_fats, cumulative_carbs, cumulative_fiber)):
        ax1.text(i, p, f'{p:.2f}г', ha='center', va='bottom', fontsize=8, color=colors['Белки'])
        ax1.text(i, f, f'{f:.2f}г', ha='center', va='bottom', fontsize=8, color=colors['Жиры'])
        ax1.text(i, c, f'{c:.2f}г', ha='center', va='bottom', fontsize=8, color=colors['Углеводы'])
        ax1.text(i, fb, f'{fb:.2f}г', ha='center', va='bottom', fontsize=8, color=colors['Клетчатка'])
    
    ax2 = plt.subplot2grid((2, 1), (1, 0))
    
    pfc_values = [total_protein, total_fat, total_carb]
    pfc_labels = ['Белки', 'Жиры', 'Углеводы']
    pfc_colors = [colors['Белки'], colors['Жиры'], colors['Углеводы']]
    
    wedges, texts, autotexts = ax2.pie(
        pfc_values,
        labels=pfc_labels,
        colors=pfc_colors,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        textprops={'fontsize': 12}
    )
    
    ax2.set_title('Соотношение БЖУ', fontsize=16, pad=20)
    ax2.axis('equal')
    
    pfc_legend = [
        f'{label}: {value:.1f}г' 
        for label, value in zip(pfc_labels, pfc_values)
    ]
    ax2.legend(wedges, pfc_legend, loc='center left', fontsize=10, bbox_to_anchor=(1, 0, 0.5, 1))
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close(fig)
    
    return buf
