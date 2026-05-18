'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import ChartCard from '@/components/dashboard/ChartCard';
import { RefreshCw, Clock, Calendar, Activity } from 'lucide-react';
import styles from './MacroAnalysis.module.css';

export default function MacroAnalysis() {
  const { t, language } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [liveData, setLiveData] = useState<any>(null);
  const [activeMacroTab, setActiveMacroTab] = useState<'gdp' | 'unemployment'>('gdp');

  const fetchData = async (forceRefresh = false) => {
    if (forceRefresh) {
      setSyncing(true);
    } else {
      setLoading(true);
    }

    try {
      const url = forceRefresh ? '/api/macro-live?refresh=true' : '/api/macro-live';
      const res = await fetch(url);
      const data = await res.json();
      if (data && data.data) {
        setLiveData(data);
      }
    } catch (err) {
      console.error('Error fetching live macro data:', err);
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p>Loading real-time market data...</p>
      </div>
    );
  }

  // Parse historical + forecast data
  const ppiData = liveData?.data?.ppi || [];
  const ppiForecast = liveData?.data?.ppi_forecast || [];

  const hdbData = liveData?.data?.hdb || [];
  const hdbForecast = liveData?.data?.hdb_forecast || [];

  const unsoldData = liveData?.data?.unsold || [];
  const unsoldForecast = liveData?.data?.unsold_forecast || [];

  const launchesData = liveData?.data?.launches || [];
  const launchesForecast = liveData?.data?.launches_forecast || [];

  const gdpData = liveData?.data?.gdp || [];
  const gdpForecast = liveData?.data?.gdp_forecast || [];

  const unemploymentData = liveData?.data?.unemployment || [];
  const unemploymentForecast = liveData?.data?.unemployment_forecast || [];

  // Formatter for forecast quarter labels
  const formatQVal = (q: string, isForecast: boolean) => {
    if (!isForecast) return q;
    return language === 'zh' ? `${q} (预测)` : `${q} (FC)`;
  };

  // 1. PPI Option (Overlaid solid & dashed lines)
  const ppiXAxis = [...ppiData.map((d: any) => d.q), ...ppiForecast.map((d: any) => formatQVal(d.q, true))];
  
  const ccrHist = [...ppiData.map((d: any) => d.ccr), ...ppiForecast.map(() => null)];
  const ccrFore = [...ppiData.map((d: any, idx: number) => idx === ppiData.length - 1 ? d.ccr : null), ...ppiForecast.map((d: any) => d.ccr)];
  
  const rcrHist = [...ppiData.map((d: any) => d.rcr), ...ppiForecast.map(() => null)];
  const rcrFore = [...ppiData.map((d: any, idx: number) => idx === ppiData.length - 1 ? d.rcr : null), ...ppiForecast.map((d: any) => d.rcr)];
  
  const ocrHist = [...ppiData.map((d: any) => d.ocr), ...ppiForecast.map(() => null)];
  const ocrFore = [...ppiData.map((d: any, idx: number) => idx === ppiData.length - 1 ? d.ocr : null), ...ppiForecast.map((d: any) => d.ocr)];

  const ppiOption = {
    tooltip: { trigger: 'axis' },
    legend: { 
      data: ['Core Central (CCR)', 'Rest of Central (RCR)', 'Outside Central (OCR)', 'Forecast Trend (CCR/RCR/OCR)'],
      bottom: 0 
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: ppiXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'Index',
      min: (value: any) => Math.floor(value.min - 5),
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      // CCR
      {
        name: 'Core Central (CCR)',
        type: 'line',
        data: ccrHist,
        itemStyle: { color: '#8b5cf6' },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Forecast Trend (CCR/RCR/OCR)',
        type: 'line',
        data: ccrFore,
        itemStyle: { color: '#8b5cf6' },
        lineStyle: { width: 2.5, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 5
      },
      // RCR
      {
        name: 'Rest of Central (RCR)',
        type: 'line',
        data: rcrHist,
        itemStyle: { color: '#3b82f6' },
        lineStyle: { width: 3.5 },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: 'Forecast Trend (CCR/RCR/OCR)',
        type: 'line',
        data: rcrFore,
        itemStyle: { color: '#3b82f6' },
        lineStyle: { width: 2.5, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 5
      },
      // OCR
      {
        name: 'Outside Central (OCR)',
        type: 'line',
        data: ocrHist,
        itemStyle: { color: '#10b981' },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Forecast Trend (CCR/RCR/OCR)',
        type: 'line',
        data: ocrFore,
        itemStyle: { color: '#10b981' },
        lineStyle: { width: 2.5, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 5
      }
    ]
  };

  // 1.5 HDB Resale price index Option
  const hdbXAxis = [...hdbData.map((d: any) => d.q), ...hdbForecast.map((d: any) => formatQVal(d.q, true))];
  const hdbHist = [...hdbData.map((d: any) => d.index), ...hdbForecast.map(() => null)];
  const hdbFore = [...hdbData.map((d: any, idx: number) => idx === hdbData.length - 1 ? d.index : null), ...hdbForecast.map((d: any) => d.index)];

  const hdbOption = {
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['HDB Resale Index', 'Forecast Index'],
      bottom: 0
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: hdbXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'Index',
      min: (value: any) => Math.floor(value.min - 2),
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: 'HDB Resale Index',
        type: 'line',
        smooth: true,
        data: hdbHist,
        itemStyle: { color: '#0284c7' },
        lineStyle: { width: 3.5 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(2, 132, 199, 0.2)' },
              { offset: 1, color: 'rgba(2, 132, 199, 0)' }
            ]
          }
        },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Forecast Index',
        type: 'line',
        smooth: true,
        data: hdbFore,
        itemStyle: { color: '#0284c7' },
        lineStyle: { width: 2.5, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 5
      }
    ]
  };

  // 2. Unsold supply Option (Semi-transparent forecasted bars)
  const unsoldXAxis = [...unsoldData.map((d: any) => d.q), ...unsoldForecast.map((d: any) => formatQVal(d.q, true))];
  const unsoldDataMapped = [
    ...unsoldData.map((d: any) => d.unsold),
    ...unsoldForecast.map((d: any) => ({
      value: d.unsold,
      itemStyle: { 
        color: 'rgba(239, 68, 68, 0.35)', 
        borderColor: '#ef4444', 
        borderWidth: 1.5, 
        borderType: 'dashed',
        borderRadius: [4, 4, 0, 0]
      }
    }))
  ];

  const unsoldOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: unsoldXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'Units',
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: 'Unsold Private Units',
        type: 'bar',
        data: unsoldDataMapped,
        itemStyle: { 
          color: '#ef4444',
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '50%'
      }
    ]
  };

  // 3. New Launches Stacked Option (Future Launches stacked with dashed styled borders)
  const launchesXAxis = [...launchesData.map((d: any) => d.q), ...launchesForecast.map((d: any) => formatQVal(d.q, true))];
  
  const ccrLaunchesMapped = [
    ...launchesData.map((d: any) => d.ccr),
    ...launchesForecast.map((d: any) => ({
      value: d.ccr,
      itemStyle: { color: 'rgba(139, 92, 246, 0.35)', borderColor: '#8b5cf6', borderWidth: 1.5, borderType: 'dashed' }
    }))
  ];
  
  const rcrLaunchesMapped = [
    ...launchesData.map((d: any) => d.rcr),
    ...launchesForecast.map((d: any) => ({
      value: d.rcr,
      itemStyle: { color: 'rgba(59, 130, 246, 0.35)', borderColor: '#3b82f6', borderWidth: 1.5, borderType: 'dashed' }
    }))
  ];
  
  const ocrLaunchesMapped = [
    ...launchesData.map((d: any) => d.ocr),
    ...launchesForecast.map((d: any) => ({
      value: d.ocr,
      itemStyle: { color: 'rgba(16, 185, 129, 0.35)', borderColor: '#10b981', borderWidth: 1.5, borderType: 'dashed', borderRadius: [4, 4, 0, 0] }
    }))
  ];

  const launchesOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { 
      data: ['CCR Launches', 'RCR Launches', 'OCR Launches'],
      bottom: 0 
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: launchesXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'Units Launched',
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: 'CCR Launches',
        type: 'bar',
        stack: 'launches',
        data: ccrLaunchesMapped,
        itemStyle: { color: '#8b5cf6' }
      },
      {
        name: 'RCR Launches',
        type: 'bar',
        stack: 'launches',
        data: rcrLaunchesMapped,
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: 'OCR Launches',
        type: 'bar',
        stack: 'launches',
        data: ocrLaunchesMapped,
        itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }
      }
    ]
  };

  // 4. Macro Tabs Options
  const gdpXAxis = [...gdpData.map((d: any) => d.year), ...gdpForecast.map((d: any) => formatQVal(d.year, true))];
  const gdpDataMapped = [
    ...gdpData.map((d: any) => d.gdp),
    ...gdpForecast.map((d: any) => ({
      value: d.gdp,
      itemStyle: {
        color: d.gdp >= 0 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)',
        borderColor: d.gdp >= 0 ? '#10b981' : '#ef4444',
        borderWidth: 1.5,
        borderType: 'dashed',
        borderRadius: [4, 4, 0, 0]
      }
    }))
  ];

  const gdpOption = {
    tooltip: { 
      trigger: 'axis',
      formatter: '{b} Year: GDP growth rate {c}%'
    },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: gdpXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'GDP Growth Rate (%)',
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: 'GDP YoY',
        type: 'bar',
        data: gdpDataMapped,
        itemStyle: { 
          color: (params: any) => params.value >= 0 ? '#10b981' : '#ef4444',
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '40%'
      }
    ]
  };

  const unemploymentXAxis = [...unemploymentData.map((d: any) => d.q), ...unemploymentForecast.map((d: any) => formatQVal(d.q, true))];
  const unemploymentHist = [...unemploymentData.map((d: any) => d.rate), ...unemploymentForecast.map(() => null)];
  const unemploymentFore = [...unemploymentData.map((d: any, idx: number) => idx === unemploymentData.length - 1 ? d.rate : null), ...unemploymentForecast.map((d: any) => d.rate)];

  const unemploymentOption = {
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['Unemployment Rate', 'Forecast Rate'],
      bottom: 0
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: unemploymentXAxis,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: { 
      type: 'value', 
      name: 'Unemployment Rate (%)',
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: 'Unemployment Rate',
        type: 'line',
        data: unemploymentHist,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.1 },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: 'Forecast Rate',
        type: 'line',
        data: unemploymentFore,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 2.5, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 5
      }
    ]
  };

  // 5. URA Pipeline Option
  const pipelineData = liveData?.data?.pipeline || { 
    ccr: { immediate: 0, medium: 0 }, 
    rcr: { immediate: 0, medium: 0 }, 
    ocr: { immediate: 0, medium: 0 },
    quarter: ''
  };

  const pipelineTitle = language === 'zh' ? 'URA 官方规划供应管线' : 'Official URA Launch Pipeline';
  const pipelineSub = language === 'zh' 
    ? `已获规划许可但尚未推出的住宅单元 (${pipelineData.quarter || '最新季度'})` 
    : `Approved private residential units pending launch (${pipelineData.quarter || 'Latest Quarter'})`;

  const pipelineCategories = language === 'zh' 
    ? ['核心中央区 (CCR)', '其他中央区 (RCR)', '中央区以外 (OCR)'] 
    : ['Core Central (CCR)', 'Rest of Central (RCR)', 'Outside Central (OCR)'];

  const pipelineOption = {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: language === 'zh' 
        ? ['短期就绪推出 (1-2季度)', '中远期规划中 (1-2年)'] 
        : ['Short-Term (Next 1-2 Quarters)', 'Medium-Term (Next 1-2 Years)'],
      bottom: 0,
      textStyle: { color: '#475569' }
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { 
      type: 'value',
      name: language === 'zh' ? '单元数' : 'Units',
      axisLine: { lineStyle: { color: '#94a3b8' } },
      splitLine: { lineStyle: { color: 'var(--card-border)' } }
    },
    yAxis: { 
      type: 'category', 
      data: pipelineCategories,
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    series: [
      {
        name: language === 'zh' ? '短期就绪推出 (1-2季度)' : 'Short-Term (Next 1-2 Quarters)',
        type: 'bar',
        data: [pipelineData.ccr?.immediate || 0, pipelineData.rcr?.immediate || 0, pipelineData.ocr?.immediate || 0],
        itemStyle: { color: '#3b82f6', borderRadius: [0, 4, 4, 0] }
      },
      {
        name: language === 'zh' ? '中远期规划中 (1-2年)' : 'Medium-Term (Next 1-2 Years)',
        type: 'bar',
        data: [pipelineData.ccr?.medium || 0, pipelineData.rcr?.medium || 0, pipelineData.ocr?.medium || 0],
        itemStyle: { color: '#8b5cf6', borderRadius: [0, 4, 4, 0] }
      }
    ]
  };

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <div>
          <h1>{t('macro.title')}</h1>
          <p className={styles.subtitle}>{t('macro.subtitle')}</p>
        </div>
      </header>

      {/* Sync Status metadata card */}
      <div className={styles.syncCard}>
        <div className={styles.syncHeader}>
          <div className={styles.statusIcon}>
            <Activity size={24} />
          </div>
          <div className={styles.syncTitleArea}>
            <h3>{t('macro.syncStatus')}</h3>
            <span className={styles.statusBadge}>Live Sync Active</span>
          </div>
        </div>

        <div className={styles.syncDetails}>
          <div className={styles.detailItem}>
            <span className={styles.detailLabel}>
              <Clock size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
              {t('macro.lastRetrieve')}
            </span>
            <span className={styles.detailValue}>{liveData?.last_retrieve_date}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailLabel}>
              <Calendar size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
              {t('macro.nextRetrieve')}
            </span>
            <span className={styles.detailValue}>{liveData?.next_retrieve_date}</span>
          </div>
        </div>

        <button 
          className={styles.syncBtn} 
          onClick={() => fetchData(true)}
          disabled={syncing}
        >
          <RefreshCw size={16} className={syncing ? 'spinner' : ''} />
          {syncing ? t('macro.syncing') : t('macro.syncNow')}
        </button>
      </div>

      {/* 2-column ECharts layout */}
      <div className={styles.contentGrid}>
        <ChartCard 
          title={t('macro.chartPpi')}
          subtitle={t('macro.chartPpiSub')}
          option={ppiOption}
        />

        <ChartCard 
          title={t('macro.chartHdb')}
          subtitle={t('macro.chartHdbSub')}
          option={hdbOption}
        />

        <ChartCard 
          title={t('macro.chartUnsold')}
          subtitle={t('macro.chartUnsoldSub')}
          option={unsoldOption}
        />

        <ChartCard 
          title={t('macro.chartLaunches')}
          subtitle={t('macro.chartLaunchesSub')}
          option={launchesOption}
        />

        <ChartCard 
          title={pipelineTitle}
          subtitle={pipelineSub}
          option={pipelineOption}
        />

        {/* Premium tab toggler card for GDP vs Unemployment */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{t('macro.chartGdp')}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t('macro.chartGdpSub')}</p>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--card-border)', padding: '0.2rem', borderRadius: '8px' }}>
              <button 
                onClick={() => setActiveMacroTab('gdp')}
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  borderRadius: '6px',
                  background: activeMacroTab === 'gdp' ? 'var(--card-bg)' : 'transparent',
                  color: activeMacroTab === 'gdp' ? 'var(--foreground)' : 'var(--text-muted)',
                  boxShadow: activeMacroTab === 'gdp' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  transition: 'all 0.2s'
                }}
              >
                GDP YoY
              </button>
              <button 
                onClick={() => setActiveMacroTab('unemployment')}
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  borderRadius: '6px',
                  background: activeMacroTab === 'unemployment' ? 'var(--card-bg)' : 'transparent',
                  color: activeMacroTab === 'unemployment' ? 'var(--foreground)' : 'var(--text-muted)',
                  boxShadow: activeMacroTab === 'unemployment' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  transition: 'all 0.2s'
                }}
              >
                Unemployment
              </button>
            </div>
          </div>

          <div style={{ height: '350px', width: '100%' }}>
            {activeMacroTab === 'gdp' ? (
              <ChartCard title="" option={gdpOption} />
            ) : (
              <ChartCard title="" option={unemploymentOption} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
