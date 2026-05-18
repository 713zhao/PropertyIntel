'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'zh';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations = {
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.marketTrends': 'Market Trends',
    'nav.landIntelligence': 'Land Intelligence',
    'nav.investment': 'Investment Strategy',
    'nav.policy': 'Policy & Benchmarks',
    'nav.macroAnalysis': 'Macro Analysis',
    'header.title': 'Property Intelligence Dashboard',
    'header.subtitle': 'Singapore Real Estate Analytics',
    'filter.region': 'Region',
    'filter.propertyType': 'Property Type',
    'filter.timeframe': 'Timeframe',
    'chart.hdbResale': 'HDB Resale Price Index',
    'chart.unsoldInventory': 'Unsold Private Residential Inventory',
    'chart.landCost': 'Historical Land Cost Timeline',
    'common.export': 'Export',
    'common.growth': 'Growth Rate',
    'common.profit': 'Profit',
    'common.price': 'Price',
    'macro.title': 'Macro Market Analysis (Live Sync)',
    'macro.subtitle': 'Real-time key macroeconomic indicators and private property benchmarks sourced from Singapore Government Open Data.',
    'macro.syncStatus': 'Weekly Auto-Sync: Active',
    'macro.lastRetrieve': 'Last Sync Time',
    'macro.nextRetrieve': 'Next Plan Sync',
    'macro.syncNow': 'Force Sync Now',
    'macro.syncing': 'Syncing...',
    'macro.chartPpi': 'Private Property Price Index (PPI) Trend',
    'macro.chartPpiSub': 'QoQ price movement across CCR, RCR, and OCR market segments.',
    'macro.chartUnsold': 'GLS Unsold Private Residential Supply',
    'macro.chartUnsoldSub': 'Total active unsold private units with planning approval.',
    'macro.chartLaunches': 'Developer Quarterly New Launches',
    'macro.chartLaunchesSub': 'New sale supply units launched by developers across regions.',
    'macro.chartGdp': 'Macro Economic Indicator: GDP & Unemployment',
    'macro.chartGdpSub': 'Correlation of annual GDP Growth Rate (YoY %) and Quarterly Unemployment Rate.',
    'macro.chartHdb': 'HDB Resale Price Index Trend',
    'macro.chartHdbSub': 'Quarterly HDB resale price index tracking the public housing market.',
  },
  zh: {
    'nav.dashboard': '仪表板',
    'nav.marketTrends': '市场趋势',
    'nav.landIntelligence': '土地情报',
    'nav.investment': '投资策略',
    'nav.policy': '政策与基准',
    'nav.macroAnalysis': '宏观市场分析',
    'header.title': '房地产情报仪表板',
    'header.subtitle': '新加坡房地产分析',
    'filter.region': '地区',
    'filter.propertyType': '物业类型',
    'filter.timeframe': '时间跨度',
    'chart.hdbResale': 'HDB 转售价格指数',
    'chart.unsoldInventory': '未售私人住宅库存',
    'chart.landCost': '历史土地成本时间表',
    'common.export': '导出',
    'common.growth': '增长率',
    'common.profit': '利润',
    'common.price': '价格',
    'macro.title': '宏观市场分析 (实时同步)',
    'macro.subtitle': '来自新加坡政府公开数据的实时关键宏观经济指标和私宅市场基准。',
    'macro.syncStatus': '周度自动更新：已激活',
    'macro.lastRetrieve': '上次同步时间',
    'macro.nextRetrieve': '下次计划同步',
    'macro.syncNow': '立即强制同步',
    'macro.syncing': '同步中...',
    'macro.chartPpi': '私宅价格指数 (PPI) 趋势',
    'macro.chartPpiSub': 'CCR、RCR 和 OCR 细分市场的季度价格走势。',
    'macro.chartUnsold': 'GLS 未售私人住宅库存量',
    'macro.chartUnsoldSub': '持有规划批准的活跃未售私宅单位总数。',
    'macro.chartLaunches': '开发商季度新盘投放量',
    'macro.chartLaunchesSub': '开发商在各地区投放的新盘销售单位数量。',
    'macro.chartGdp': '宏观经济指标：GDP 与失业率',
    'macro.chartGdpSub': '年度 GDP 增长率 (YoY %) 与季度整体失业率的关联趋势。',
    'macro.chartHdb': 'HDB 转售价格指数走势',
    'macro.chartHdbSub': '跟踪新加坡公共组屋（HDB）转售价格指数的季度变动走势。',
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('zh');

  const t = (key: string) => {
    return (translations[language] as any)[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
