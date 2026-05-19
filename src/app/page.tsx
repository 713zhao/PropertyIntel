'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import ChartCard from '@/components/dashboard/ChartCard';
import { unsoldInventory } from '@/constants/mockData';
import { 
  TrendingUp, 
  Home, 
  BarChart3, 
  DollarSign 
} from 'lucide-react';
import styles from './page.module.css';
import { API_BASE_URL } from '@/config/api';

export default function Dashboard() {
  const { t, language } = useLanguage();
  const [propertyData, setPropertyData] = useState<any[]>([]);
  const [stats, setStats] = useState({ growth: '5.3%', inventory: '21,900', landCost: '$1,420' });

  useEffect(() => {
    // Fetch Macro Insights (contains both indices)
    fetch(`${API_BASE_URL}/api/macro-insights`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setPropertyData(data);
          
          // Calculate growth from last 4 quarters (YoY approx)
          if (data.length > 4) {
            const current = data[data.length - 1].hdb_index;
            const lastYear = data[data.length - 5].hdb_index;
            const growth = ((current - lastYear) / lastYear * 100).toFixed(1);
            setStats(prev => ({ ...prev, growth: `+${growth}%` }));
          }
        }
      })
      .catch(err => console.error('Error fetching property data:', err));
  }, []);

  const last40Quarters = propertyData.slice(-40);
  const quarters = last40Quarters.map(d => d.quarter);
  const hdbValues = last40Quarters.map(d => d.hdb_index);
  const privateValues = last40Quarters.map(d => d.private_index);

  const lastUpdatedText = language === 'zh' ? '上次更新: 2026年5月' : 'Last updated: May 2026';
  
  // Stat Card labels
  const avgPriceGrowthLabel = language === 'zh' ? '年均价格增长' : 'Avg Price Growth';
  const totalInventoryLabel = language === 'zh' ? '总未售库存量' : 'Total Inventory';
  const avgLandCostLabel = language === 'zh' ? '平均土地成本' : 'Avg Land Cost';
  const activeBidsLabel = language === 'zh' ? '活跃竞投数' : 'Active Bids';

  const yoyTrendLabel = language === 'zh' ? '↑ 同比增长趋势' : '↑ YoY Trend';
  const lqTrendLabel = language === 'zh' ? '↓ 比上季度减 3.5%' : '↓ 3.5% from LQ';
  const stableTrendLabel = language === 'zh' ? '↑ 稳定趋势' : '↑ Stable Trend';
  const stableLabel = language === 'zh' ? '- 稳定' : '- Stable';

  const marketPriceTrendTitle = language === 'zh' ? '公共与私有住宅价格指数走势' : 'Public vs Private Property Price Index';
  const hdbResaleSub = language === 'zh' 
    ? '历史不同时期的组屋与私宅指数年均增长率走势关联' 
    : 'Comparison of HDB Resale and Private Property Index trends';
  
  const unsoldInventorySub = language === 'zh'
    ? '按市场细分地区划分的季度未售私住宅库存量 (CCR, RCR, OCR)'
    : 'Quarterly inventory levels by region (CCR, RCR, OCR)';

  const hdbIndexLabel = language === 'zh' ? 'HDB 转售价格指数' : 'HDB Resale Index';
  const privateIndexLabel = language === 'zh' ? '私宅价格指数' : 'Private Property Index';

  const propertyOption = {
    tooltip: { trigger: 'axis' },
    legend: {
      data: [hdbIndexLabel, privateIndexLabel],
      top: 10,
      textStyle: { color: '#475569' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 70, containLabel: true },
    xAxis: { type: 'category', data: quarters },
    yAxis: { type: 'value', name: language === 'zh' ? '指数值' : 'Index Value', min: 'dataMin' },
    series: [
      {
        name: hdbIndexLabel,
        type: 'line',
        data: hdbValues,
        smooth: true,
        lineStyle: { color: '#38bdf8', width: 4 },
        itemStyle: { color: '#38bdf8' }
      },
      {
        name: privateIndexLabel,
        type: 'line',
        data: privateValues,
        smooth: true,
        lineStyle: { color: '#fbbf24', width: 4 },
        itemStyle: { color: '#fbbf24' }
      }
    ]
  };

  const inventoryOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { 
      bottom: 0,
      textStyle: { color: '#475569' }
    },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: unsoldInventory.quarters },
    yAxis: { type: 'value', name: language === 'zh' ? '单位数' : 'Units' },
    series: [
      { name: language === 'zh' ? '核心中央区 (CCR)' : 'CCR', type: 'bar', stack: 'total', data: unsoldInventory.ccr, itemStyle: { color: '#0f172a' } },
      { name: language === 'zh' ? '其他中央区 (RCR)' : 'RCR', type: 'bar', stack: 'total', data: unsoldInventory.rcr, itemStyle: { color: '#38bdf8' } },
      { name: language === 'zh' ? '中央区以外 (OCR)' : 'OCR', type: 'bar', stack: 'total', data: unsoldInventory.ocr, itemStyle: { color: '#fbbf24' } }
    ]
  };

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <div className={styles.welcome}>
          <h1>{t('header.title')}</h1>
          <p>{t('header.subtitle')}</p>
        </div>
        <div className={styles.dateRange}>
          {lastUpdatedText}
        </div>
      </header>

      <section className={styles.statsGrid}>
        <div className={`card ${styles.statCard}`}>
          <div className={styles.statIcon} style={{ background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8' }}>
            <TrendingUp size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>{avgPriceGrowthLabel}</span>
            <span className={styles.statValue}>{stats.growth}</span>
            <span className={styles.statTrend} style={{ color: 'var(--success)' }}>{yoyTrendLabel}</span>
          </div>
        </div>

        <div className={`card ${styles.statCard}`}>
          <div className={styles.statIcon} style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
            <Home size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>{totalInventoryLabel}</span>
            <span className={styles.statValue}>{stats.inventory}</span>
            <span className={styles.statTrend} style={{ color: 'var(--danger)' }}>{lqTrendLabel}</span>
          </div>
        </div>

        <div className={`card ${styles.statCard}`}>
          <div className={styles.statIcon} style={{ background: 'rgba(251, 191, 36, 0.1)', color: '#fbbf24' }}>
            <DollarSign size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>{avgLandCostLabel}</span>
            <span className={styles.statValue}>{stats.landCost} psf</span>
            <span className={styles.statTrend} style={{ color: 'var(--success)' }}>{stableTrendLabel}</span>
          </div>
        </div>

        <div className={`card ${styles.statCard}`}>
          <div className={styles.statIcon} style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
            <BarChart3 size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>{activeBidsLabel}</span>
            <span className={styles.statValue}>8.4</span>
            <span className={styles.statTrend} style={{ color: 'var(--text-muted)' }}>{stableLabel}</span>
          </div>
        </div>
      </section>

      <section className={styles.chartsGrid}>
        <ChartCard 
          title={marketPriceTrendTitle}
          subtitle={hdbResaleSub}
          option={propertyOption}
        />
        <ChartCard 
          title={t('chart.unsoldInventory')}
          subtitle={unsoldInventorySub}
          option={inventoryOption}
        />
      </section>
    </div>
  );
}
