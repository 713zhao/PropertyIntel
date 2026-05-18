'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import ChartCard from '@/components/dashboard/ChartCard';
import styles from './LandIntelligence.module.css';

export default function LandIntelligence() {
  const { t, language } = useLanguage();
  const [data, setData] = useState<any>({ gls_history: [], launch_correlation: [] });

  useEffect(() => {
    fetch('/api/land-intelligence')
      .then(res => res.json())
      .then(d => {
        if (d.gls_history) {
          setData(d);
        }
      })
      .catch(err => console.error('Error fetching land intelligence:', err));
  }, []);

  const title1 = language === 'zh' ? '历史土地成本变化趋势' : 'Historical Land Cost Timeline';
  const sub1 = language === 'zh' 
    ? '跟踪各区域政府售地计划 (GLS) 中标成交价 ($ psf ppr)' 
    : 'Tracking GLS awarded prices ($ psf ppr) across regions';

  const title2 = language === 'zh' ? '面粉与面包：土地成本与楼盘售价关联' : 'Land Cost vs. Launch Price Correlation';
  const sub2 = language === 'zh'
    ? '分析地皮收购成本与楼盘最终开盘售价之间的差额空间'
    : 'Analyzing the spread between land acquisition and final selling price';

  const caseStudyTitle = language === 'zh' ? '近年新盘推出价格基准参考 (2024-2026)' : 'New Launch Price Benchmarks (2024-2026)';
  const thProject = language === 'zh' ? '项目名称' : 'Project Name';
  const thRegion = language === 'zh' ? '所在区域' : 'Region';
  const thLandCost = language === 'zh' ? '地皮收购成本' : 'Land Cost';
  const thLaunchPrice = language === 'zh' ? '实际/预估推出均价' : 'Est./Actual Launch Price';
  const thSpread = language === 'zh' ? '溢价率 (Spread)' : 'Estimated Spread';

  const ccrLabel = language === 'zh' ? '核心中央区 (CCR)' : 'CCR';
  const rcrLabel = language === 'zh' ? '其他中央区 (RCR)' : 'RCR';
  const ocrLabel = language === 'zh' ? '中央区以外 (OCR)' : 'OCR';

  const allYears = [...new Set(data.gls_history.map((d: any) => d.year))].sort();

  const timelineOption = {
    tooltip: { trigger: 'axis' },
    legend: { 
      data: [ccrLabel, rcrLabel, ocrLabel],
      top: 10,
      textStyle: { color: '#475569' }
    },
    grid: { top: 70, bottom: 40, left: 60, right: 30 },
    xAxis: { type: 'category', data: allYears },
    yAxis: { 
      type: 'value', 
      name: language === 'zh' ? '价格 ($ PSF PPR)' : '$ PSF PPR', 
      min: 600,
      splitLine: { lineStyle: { color: 'var(--card-border)' } }
    },
    series: ['CCR', 'RCR', 'OCR'].map(region => {
      // Correctly map values to years to avoid alignment issues
      const seriesData = allYears.map(year => {
        const entry = data.gls_history.find((d: any) => d.region === region && d.year === year);
        return entry ? entry.psf_ppr : null;
      });

      return {
        name: region === 'CCR' ? ccrLabel : region === 'RCR' ? rcrLabel : ocrLabel,
        type: 'line',
        data: seriesData,
        smooth: true,
        connectNulls: true, // Connect lines across years with missing data
        symbolSize: 8
      };
    })
  };

  const landCostLabel = language === 'zh' ? '土地招标成本 (PSF PPR)' : 'Land Cost (PSF PPR)';
  const launchPriceLabel = language === 'zh' ? '开盘售价 (PSF)' : 'Launch Price (PSF)';

  const correlationOption = {
    tooltip: { trigger: 'axis' },
    legend: { 
      data: [landCostLabel, launchPriceLabel],
      top: 10,
      textStyle: { color: '#475569' }
    },
    grid: { top: 70, bottom: 40, left: 60, right: 30 },
    xAxis: { type: 'category', data: data.launch_correlation.map((d: any) => d.project_name) },
    yAxis: { 
      type: 'value', 
      name: language === 'zh' ? '价格 ($ PSF)' : '$ PSF',
      splitLine: { lineStyle: { color: 'var(--card-border)' } }
    },
    series: [
      {
        name: landCostLabel,
        type: 'bar',
        data: data.launch_correlation.map((d: any) => d.land_cost_psf_ppr),
        itemStyle: { color: '#fbbf24' }
      },
      {
        name: launchPriceLabel,
        type: 'bar',
        data: data.launch_correlation.map((d: any) => d.avg_price_psf),
        itemStyle: { color: '#38bdf8' }
      }
    ]
  };

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <h1>{t('nav.landIntelligence')}</h1>
      </header>

      <div className={styles.chartsGrid}>
        <ChartCard 
          title={title1}
          subtitle={sub1}
          option={timelineOption}
        />
        <ChartCard 
          title={title2}
          subtitle={sub2}
          option={correlationOption}
        />
      </div>

      <div className={`card ${styles.caseStudy}`}>
        <h3>{caseStudyTitle}</h3>
        <table className={styles.table} style={{ width: '100%', marginTop: '1rem' }}>
          <thead>
            <tr>
              <th>{thProject}</th>
              <th>{thRegion}</th>
              <th>{thLandCost}</th>
              <th>{thLaunchPrice}</th>
              <th>{thSpread}</th>
            </tr>
          </thead>
          <tbody>
            {data.launch_correlation.slice(-5).reverse().map((row: any, i: number) => {
              const regText = row.region === 'CCR' ? ccrLabel : row.region === 'RCR' ? rcrLabel : ocrLabel;
              return (
                <tr key={i}>
                  <td>{row.project_name}</td>
                  <td>{regText}</td>
                  <td>${row.land_cost_psf_ppr} psf ppr</td>
                  <td style={{ fontWeight: 'bold', color: 'var(--accent)' }}>${row.avg_price_psf} psf</td>
                  <td>{((row.avg_price_psf / row.land_cost_psf_ppr - 1) * 100).toFixed(0)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
