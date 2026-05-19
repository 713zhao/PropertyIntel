'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import ChartCard from '@/components/dashboard/ChartCard';
import styles from './MarketTrends.module.css';
import { API_BASE_URL } from '@/config/api';

export default function MarketTrends() {
  const { t, language } = useLanguage();
  const [macroData, setMacroData] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/macro-insights`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setMacroData(data);
        }
      })
      .catch(err => console.error('Error fetching macro insights:', err));
  }, []);

  const last40Quarters = macroData.slice(-40);
  const quarters = last40Quarters.map(d => d.quarter);

  // Localized headers and text
  const title1 = language === 'zh' ? '组屋与私宅价格差距走势关联' : 'Market Price Gap (Private vs HDB)';
  const sub1 = language === 'zh'
    ? '分析公共组屋转售价格指数与私人住宅价格指数之间的比率变动'
    : 'Correlation between public and private property prices';

  const title2 = language === 'zh' ? '购房负担能力指数走势' : 'Affordability Index Trend';
  const sub2 = language === 'zh'
    ? '家庭月入中位数与私住宅价格指数之比值趋势（比值越高，负担能力越强）'
    : 'Ratio of Median Household Income to Private Property Index';

  const title3 = language === 'zh' ? '常住人口增长趋势（潜在住房需求）' : 'Population Growth (Demand Proxy)';
  const sub3 = language === 'zh'
    ? '居民总人口历史变动趋势，用以评估长期房地产核心基本面需求'
    : 'Total resident population trends to understand underlying demand';

  const tableTitle = language === 'zh' ? '近年市场价格走势基准数据' : 'Recent Market Benchmarks';
  const thQuarter = language === 'zh' ? '季度' : 'Quarter';
  const thHdb = language === 'zh' ? '组屋指数' : 'HDB Index';
  const thPrivate = language === 'zh' ? '私宅指数' : 'Private Index';
  const thRatio = language === 'zh' ? '价格比率 (倍数)' : 'Price Ratio';

  // Localized Chart options
  const hdbIndexLabel = language === 'zh' ? 'HDB 价格指数' : 'HDB Index';
  const privateIndexLabel = language === 'zh' ? '私宅价格指数' : 'Private Index';
  const priceGapLabel = language === 'zh' ? '价格差距比率 (倍数)' : 'Price Gap Ratio';

  const priceGapOption = {
    tooltip: { trigger: 'axis' },
    legend: { 
      data: [hdbIndexLabel, privateIndexLabel, priceGapLabel],
      top: 10,
      textStyle: { color: '#475569' }
    },
    grid: { top: 70, bottom: 40, left: 50, right: 50 },
    xAxis: { type: 'category', data: quarters },
    yAxis: [
      { type: 'value', name: language === 'zh' ? '指数值' : 'Index', splitLine: { lineStyle: { color: 'var(--card-border)' } } },
      { type: 'value', name: language === 'zh' ? '比率 (倍)' : 'Ratio', splitLine: { show: false } }
    ],
    series: [
      {
        name: hdbIndexLabel,
        type: 'line',
        data: last40Quarters.map(d => d.hdb_index),
        itemStyle: { color: '#38bdf8' }
      },
      {
        name: privateIndexLabel,
        type: 'line',
        data: last40Quarters.map(d => d.private_index),
        itemStyle: { color: '#fbbf24' }
      },
      {
        name: priceGapLabel,
        type: 'line',
        yAxisIndex: 1,
        data: last40Quarters.map(d => d.price_gap),
        lineStyle: { type: 'dashed' },
        itemStyle: { color: '#ef4444' }
      }
    ]
  };

  const affordabilityOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: quarters },
    yAxis: { 
      type: 'value', 
      name: language === 'zh' ? '负担能力指数' : 'Affordability Index',
      splitLine: { lineStyle: { color: 'var(--card-border)' } }
    },
    series: [
      {
        name: language === 'zh' ? '负担能力指数 (家庭月入中位数 / 私宅指数)' : 'Affordability (Income/Price)',
        type: 'line',
        smooth: true,
        data: last40Quarters.map(d => d.affordability_index),
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: '#10b981' }
      }
    ]
  };

  const populationOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: quarters },
    yAxis: { 
      type: 'value', 
      name: language === 'zh' ? '常住人口' : 'Population', 
      min: 'dataMin',
      splitLine: { lineStyle: { color: 'var(--card-border)' } }
    },
    series: [
      {
        name: language === 'zh' ? '常住人口总数' : 'Total Population',
        type: 'bar',
        data: last40Quarters.map(d => d.total_population),
        itemStyle: { color: '#6366f1' }
      }
    ]
  };

  const yoyTable = macroData.slice(-5).reverse().map(d => {
    return {
      year: d.quarter,
      hdb: d.hdb_index,
      private: d.private_index,
      gap: d.price_gap
    };
  });

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <h1>{t('nav.marketTrends')}</h1>
      </header>

      <div className={styles.contentGrid}>
        <ChartCard 
          title={title1}
          subtitle={sub1}
          option={priceGapOption}
        />

        <ChartCard 
          title={title2}
          subtitle={sub2}
          option={affordabilityOption}
        />

        <ChartCard 
          title={title3}
          subtitle={sub3}
          option={populationOption}
        />

        <div className={`card ${styles.tableCard}`}>
          <h3>{tableTitle}</h3>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{thQuarter}</th>
                <th>{thHdb}</th>
                <th>{thPrivate}</th>
                <th>{thRatio}</th>
              </tr>
            </thead>
            <tbody>
              {yoyTable.map((row) => (
                <tr key={row.year}>
                  <td>{row.year}</td>
                  <td>{row.hdb}</td>
                  <td>{row.private}</td>
                  <td>{row.gap}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
