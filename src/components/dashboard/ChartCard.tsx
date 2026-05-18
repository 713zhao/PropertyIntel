'use client';

import ReactECharts from 'echarts-for-react';
import styles from './ChartCard.module.css';
import { Download, Maximize2, MoreHorizontal } from 'lucide-react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  option: any;
  loading?: boolean;
}

const ChartCard = ({ title, subtitle, option, loading }: ChartCardProps) => {
  return (
    <div className={`card ${styles.chartCard} fade-in`}>
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <h3>{title}</h3>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
        <div className={styles.actions}>
          <button className={styles.actionBtn} title="Export"><Download size={16} /></button>
          <button className={styles.actionBtn} title="Fullscreen"><Maximize2 size={16} /></button>
          <button className={styles.actionBtn} title="More"><MoreHorizontal size={16} /></button>
        </div>
      </div>
      <div className={styles.chartArea}>
        {loading ? (
          <div className={styles.loader}>Loading...</div>
        ) : (
          <ReactECharts 
            option={option} 
            style={{ height: '350px', width: '100%' }}
            notMerge={true}
          />
        )}
      </div>
    </div>
  );
};

export default ChartCard;
