'use client';

import { useLanguage } from '@/context/LanguageContext';
import styles from './InvestmentStrategy.module.css';
import { ChevronRight, DollarSign, PieChart, Landmark } from 'lucide-react';

export default function InvestmentStrategy() {
  const { t, language } = useLanguage();

  const journeyStages = [
    { 
      name: language === 'zh' ? '新组屋 (HDB BTO)' : 'HDB BTO', 
      icon: <Home size={20} />, 
      age: '25-30', 
      capital: language === 'zh' ? '5万新币' : '$50k' 
    },
    { 
      name: language === 'zh' ? '转售组屋 (Resale HDB)' : 'Resale HDB', 
      icon: <Building size={20} />, 
      age: '35-40', 
      capital: language === 'zh' ? '30万新币' : '$300k' 
    },
    { 
      name: language === 'zh' ? '私人住宅 (Private)' : 'Private Property', 
      icon: <Landmark size={20} />, 
      age: '45-50', 
      capital: language === 'zh' ? '80万新币' : '$800k' 
    },
    { 
      name: language === 'zh' ? '豪宅/高价值物业' : 'Higher Value Prop', 
      icon: <TrendingUp size={20} />, 
      age: '55+', 
      capital: language === 'zh' ? '150万新币+' : '$1.5M+' 
    },
  ];

  const section1Title = language === 'zh' ? '置业与资产增值进阶之路' : 'Property Capital Building Journey';
  const section1Sub = language === 'zh' 
    ? '科学规划从首套自住房到高价值投资物业的资金阶梯与增值轨迹' 
    : 'Visualizing the path from first home to high-value investment';

  const ageText = language === 'zh' ? '年龄阶段' : 'Age';
  const equityText = language === 'zh' ? '预估股本/资产' : 'Est. Equity';

  const calcTitle = language === 'zh' ? '投资回报估算模型' : 'Estimated Returns Model';
  const labelPrice = language === 'zh' ? '物业购买总价' : 'Purchase Price';
  const labelCash = language === 'zh' ? '首期现金支出' : 'Initial Cash Outlay';
  const labelPeriod = language === 'zh' ? '计划持有年限 (年)' : 'Holding Period (Years)';
  const calcBtnText = language === 'zh' ? '开始计算净回报' : 'Calculate Net Returns';

  const projTitle = language === 'zh' ? '财务回报预测指标' : 'Financial Projections';
  const proceedText = language === 'zh' ? '售出套现所得' : 'Selling Proceeds';
  const mortgageText = language === 'zh' ? '房贷及相关利息成本' : 'Mortgage Costs';
  const profitText = language === 'zh' ? '预估净利润总额' : 'Estimated Net Profit';
  const roiText = language === 'zh' ? '投资回报率' : 'ROI';

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <h1>{t('nav.investment')}</h1>
      </header>

      <section className={`card ${styles.journeySection}`}>
        <h3>{section1Title}</h3>
        <p className={styles.subtitle}>{section1Sub}</p>
        
        <div className={styles.timeline}>
          {journeyStages.map((stage, index) => (
            <div key={stage.name} className={styles.stage}>
              <div className={styles.stageIcon}>{stage.icon || <DollarSign size={20} />}</div>
              <div className={styles.stageInfo}>
                <span className={styles.stageName}>{stage.name}</span>
                <span className={styles.stageAge}>{ageText}: {stage.age}</span>
                <span className={styles.stageCapital}>{equityText}: {stage.capital}</span>
              </div>
              {index < journeyStages.length - 1 && <ChevronRight className={styles.connector} />}
            </div>
          ))}
        </div>
      </section>

      <div className={styles.modelGrid}>
        <div className={`card ${styles.calculator}`}>
          <h3>{calcTitle}</h3>
          <div className={styles.inputGroup}>
            <label>{labelPrice}</label>
            <input type="text" defaultValue="$1,500,000" />
          </div>
          <div className={styles.inputGroup}>
            <label>{labelCash}</label>
            <input type="text" defaultValue="$375,000" />
          </div>
          <div className={styles.inputGroup}>
            <label>{labelPeriod}</label>
            <input type="number" defaultValue="5" />
          </div>
          <button className={styles.calcBtn}>{calcBtnText}</button>
        </div>

        <div className={`card ${styles.results}`}>
          <h3>{projTitle}</h3>
          <div className={styles.resultItem}>
            <span>{proceedText}</span>
            <span className={styles.resValue}>$1,850,000</span>
          </div>
          <div className={styles.resultItem}>
            <span>{mortgageText}</span>
            <span className={styles.resValue}>$120,000</span>
          </div>
          <hr className={styles.divider} />
          <div className={`${styles.resultItem} ${styles.total}`}>
            <span>{profitText}</span>
            <span className={styles.resValue}>$230,000</span>
          </div>
          <div className={styles.roi}>
            {roiText}: <span className={styles.roiValue}>61.3%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper icons since I missed some imports
const Home = ({ size }: { size: number }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
const Building = ({ size }: { size: number }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>;
const TrendingUp = ({ size }: { size: number }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>;
