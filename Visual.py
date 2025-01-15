from google.colab import files
uploaded = files.upload()

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

file_paths_updated = [
    'Ocean2021.csv',
    'Ocean2023.csv',
    'Ocean2022.csv',
    'Ocean2024.csv',
    'Ocean2020.csv'
    '109.01.csv',
    '111.01.csv',
    '112.01.csv',
    '113.01.csv',
    '110.01.csv',
]

# Column translations
column_translations = {
    '縣市別': 'County',
    '清理範圍(處)': 'CleanupArea',
    '清理次數(次)': 'CleanupFrequency',
    '參與人數(人次)': 'Participants',
    '海洋廢棄物來源(噸)_海漂': 'MarineWaste_Floating',
    '海洋廢棄物來源(噸)_海底': 'MarineWaste_Seabed',
    '海洋廢棄物來源(噸)_淨灘': 'MarineWaste_BeachCleanup',
    '海洋廢棄物來源(噸)_船舶人員產出': 'MarineWaste_ShipGenerated',
    '海洋廢棄物來源(噸)_岸上定點設置垃圾桶': 'MarineWaste_BinsOnshore',
    '清理數量分類(噸)_寶特瓶': 'Cleanup_PETBottles',
    '清理數量分類(噸)_鐵罐': 'Cleanup_IronCans',
    '清理數量分類(噸)_鋁罐': 'Cleanup_AluminumCans',
    '清理數量分類(噸)_玻璃瓶': 'Cleanup_GlassBottles',
    '清理數量分類(噸)_廢紙': 'Cleanup_WastePaper',
    '清理數量分類(噸)_竹木': 'Cleanup_BambooWood',
    '清理數量分類(噸)_保麗龍': 'Cleanup_Styrofoam',
    '清理數量分類(噸)_廢漁具漁網': 'Cleanup_FishingGear',
    '清理數量分類(噸)_無法分類廢棄物': 'Cleanup_UncategorizedWaste',
    'Year': 'Year'
}

dataframes_final = []

for file_path in file_paths_updated:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            header_row = next(i for i, line in enumerate(f) if '縣市別' in line)
        
        if re.search(r'Ocean(\d{4})', file_path):
            year_match = re.search(r'(\d{4})', file_path)
            year = int(year_match.group(0)) if year_match else None
        elif re.search(r'(\d{3})\.\d{2}', file_path):
            year_match = re.search(r'(\d{3})', file_path)
            year = int(year_match.group(0)) + 1911 if year_match else None

        df = pd.read_csv(file_path, header=header_row, encoding='utf-8')
        df.columns = [col.strip().replace(' ', '').replace('\n', '') for col in df.columns]
        df.rename(columns=column_translations, inplace=True)
        if 'County' not in df.columns:
            df['County'] = 'Unknown'
        if year:
            df['Year'] = year
        dataframes_final.append(df)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")

combined_data_final = pd.concat(dataframes_final, ignore_index=True)

for col in combined_data_final.columns:
    if combined_data_final[col].dtype == 'object':
        combined_data_final[col] = combined_data_final[col].str.replace(',', '').str.strip()
        combined_data_final[col] = pd.to_numeric(combined_data_final[col], errors='coerce')

combined_data_final.dropna(subset=['Year'], inplace=True)

# Visualization 1: Heatmap of correlations
correlation_matrix = combined_data_final.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.show()

# Visualization 2: Yearly trends of cleanup metrics
key_columns = ['CleanupArea', 'CleanupFrequency', 'Participants']
if set(key_columns).issubset(combined_data_final.columns):
    yearly_trends = combined_data_final.groupby('Year')[key_columns].sum()
    yearly_trends.plot(kind='line', figsize=(12, 6), marker='o')
    plt.title('Yearly Trends: Cleanup Area, Frequency, and Participants')
    plt.xlabel('Year')
    plt.ylabel('Counts')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Visualization 3: Marine waste sources
waste_sources = [
    'MarineWaste_Floating',
    'MarineWaste_Seabed',
    'MarineWaste_BeachCleanup',
    'MarineWaste_ShipGenerated',
    'MarineWaste_BinsOnshore'
]
valid_waste_sources = [col for col in waste_sources if col in combined_data_final.columns]
if valid_waste_sources:
    waste_trends = combined_data_final.groupby('Year')[valid_waste_sources].sum()
    waste_trends.plot(kind='line', figsize=(12, 6), marker='o')
    plt.title('Yearly Trends: Marine Waste Sources')
    plt.xlabel('Year')
    plt.ylabel('Tons')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Visualization 4: Cleanup categories
cleanup_categories = [
    'Cleanup_PETBottles',
    'Cleanup_IronCans',
    'Cleanup_AluminumCans',
    'Cleanup_GlassBottles',
    'Cleanup_WastePaper',
    'Cleanup_BambooWood',
    'Cleanup_Styrofoam',
    'Cleanup_FishingGear',
    'Cleanup_UncategorizedWaste'
]
valid_cleanup_categories = [col for col in cleanup_categories if col in combined_data_final.columns]
if valid_cleanup_categories:
    cleanup_trends = combined_data_final.groupby('Year')[valid_cleanup_categories].sum()
    cleanup_trends.plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title('Yearly Trends: Cleanup Categories')
    plt.xlabel('Year')
    plt.ylabel('Tons')
    plt.legend(title='Categories')
    plt.tight_layout()
    plt.show()

# Visualization 5: Total cleanup area by county
if 'CleanupArea' in combined_data_final.columns:
    county_cleanup = combined_data_final.groupby('County')['CleanupArea'].sum()
    if not county_cleanup.empty:  # Check if the DataFrame is not empty
        county_cleanup.sort_values().plot(kind='barh', figsize=(10, 8), color='skyblue')
        plt.title('Total Cleanup Area by County')
        plt.xlabel('Cleanup Area')
        plt.ylabel('County')
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for CleanupArea by County.")


# Visualization 6: Proportions of marine waste sources in recent years
if valid_waste_sources:
    recent_waste_totals = combined_data_final[combined_data_final['Year'] >= 2020][valid_waste_sources].sum()
    recent_waste_totals.plot(kind='pie', autopct='%1.1f%%', figsize=(8, 8))
    plt.title('Proportions of Marine Waste Sources (2020 and beyond)')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

# Additional visualizations can be added here if needed.

# Visualization 7: Top 5 counties with the most cleanup frequency
# Visualization: Top 5 counties with the most cleanup frequency
if 'CleanupFrequency' in combined_data_final.columns:
    top_counties_frequency = (
        combined_data_final.groupby('County')['CleanupFrequency']
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    if not top_counties_frequency.empty:  # Check if data is not empty
        top_counties_frequency.plot(kind='bar', figsize=(10, 6), color='coral')
        plt.title('Top 5 Counties by Cleanup Frequency')
        plt.xlabel('County')
        plt.ylabel('Cleanup Frequency')
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for CleanupFrequency by County.")
else:
    print("Column 'CleanupFrequency' not found in the dataset.")


# Visualization 8: Yearly trends of participation across top 5 counties
if {'Participants', 'Year', 'County'}.issubset(combined_data_final.columns):
    # Identify top counties by total participation
    top_counties_participation = (
        combined_data_final.groupby('County')['Participants']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )
    
    # Filter data for the top counties
    filtered_data = combined_data_final[combined_data_final['County'].isin(top_counties_participation)]
    
    # Check if filtered data is non-empty
    if not filtered_data.empty:
        # Group data by Year and County
        yearly_participation = filtered_data.groupby(['Year', 'County'])['Participants'].sum().unstack()
        
        # Check if there is numeric data to plot
        if not yearly_participation.empty:
            yearly_participation.plot(kind='line', figsize=(12, 8), marker='o')
            plt.title('Yearly Participation Trends in Top 5 Counties')
            plt.xlabel('Year')
            plt.ylabel('Participants')
            plt.legend(title='County')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print("No numeric data to plot for participation trends.")
    else:
        print("Filtered data is empty; no participation trends available.")
else:
    print("Required columns (Participants, Year, County) are not in the dataset.")


# Visualization 9: Proportion of cleanup categories in recent years
cleanup_categories = [
    'Cleanup_PETBottles',
    'Cleanup_IronCans',
    'Cleanup_AluminumCans',
    'Cleanup_GlassBottles',
    'Cleanup_WastePaper',
    'Cleanup_BambooWood',
    'Cleanup_Styrofoam',
    'Cleanup_FishingGear',
    'Cleanup_UncategorizedWaste'
]
valid_cleanup_categories = [col for col in cleanup_categories if col in combined_data_final.columns]
if valid_cleanup_categories:
    recent_data = combined_data_final[combined_data_final['Year'] >= 2020][valid_cleanup_categories].sum()
    recent_data.plot(kind='pie', autopct='%1.1f%%', figsize=(8, 8))
    plt.title('Proportion of Cleanup Categories (2020 and Beyond)')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

# Visualization 10: Heatmap of yearly totals for waste categories
if valid_cleanup_categories:
    yearly_totals = combined_data_final.groupby('Year')[valid_cleanup_categories].sum()
    plt.figure(figsize=(12, 8))
    sns.heatmap(yearly_totals, annot=True, fmt='.1f', cmap='YlGnBu')
    plt.title('Yearly Totals for Cleanup Categories')
    plt.xlabel('Category')
    plt.ylabel('Year')
    plt.tight_layout()
    plt.show()

# Visualization 11: Total marine waste sources by year
waste_sources = [
    'MarineWaste_Floating',
    'MarineWaste_Seabed',
    'MarineWaste_BeachCleanup',
    'MarineWaste_ShipGenerated',
    'MarineWaste_BinsOnshore'
]
valid_waste_sources = [col for col in waste_sources if col in combined_data_final.columns]
if valid_waste_sources:
    total_waste_yearly = combined_data_final.groupby('Year')[valid_waste_sources].sum()
    total_waste_yearly.plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title('Total Marine Waste Sources by Year')
    plt.xlabel('Year')
    plt.ylabel('Tons')
    plt.legend(title='Waste Sources')
    plt.tight_layout()
    plt.show()

# Visualization 12: Monthly trends in recent years (if date is available)
if 'Date' in combined_data_final.columns:
    combined_data_final['Month'] = pd.to_datetime(combined_data_final['Date'], errors='coerce').dt.month
    if 'CleanupArea' in combined_data_final.columns:
        monthly_trends = combined_data_final.groupby(['Month', 'Year'])['CleanupArea'].sum().unstack()
        monthly_trends.plot(kind='line', figsize=(12, 8), marker='o')
        plt.title('Monthly Trends of Cleanup Area')
        plt.xlabel('Month')
        plt.ylabel('Cleanup Area')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Visualization 13: Relationship between participants and cleanup frequency
if {'Participants', 'CleanupFrequency'}.issubset(combined_data_final.columns):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=combined_data_final, x='Participants', y='CleanupFrequency', hue='Year', palette='cool')
    plt.title('Participants vs Cleanup Frequency')
    plt.xlabel('Participants')
    plt.ylabel('Cleanup Frequency')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Visualization 14: Top 5 counties with the highest total waste cleaned
# Visualization: Top 5 counties with the highest total waste cleaned
if valid_cleanup_categories:
    combined_data_final['Total_Cleanup'] = combined_data_final[valid_cleanup_categories].sum(axis=1)
    top_waste_counties = (
        combined_data_final.groupby('County')['Total_Cleanup']
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    if not top_waste_counties.empty:  # Check if data is not empty
        top_waste_counties.plot(kind='bar', figsize=(10, 6), color='teal')
        plt.title('Top 5 Counties by Total Waste Cleaned')
        plt.xlabel('County')
        plt.ylabel('Total Waste (Tons)')
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for Total Cleanup by County.")
else:
    print("No valid cleanup categories found for total cleanup calculation.")