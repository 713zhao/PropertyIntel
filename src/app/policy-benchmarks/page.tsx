'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import styles from './PolicyBenchmarks.module.css';
import { ShieldCheck, Calendar, Users, Zap } from 'lucide-react';

export default function PolicyBenchmarks() {
  const { t, language } = useLanguage();
  const [topTrans, setTopTrans] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/transactions?limit=20')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setTopTrans(data);
        }
      })
      .catch(err => console.error('Error fetching transactions:', err));
  }, []);

  const policies = [
    { 
      title: language === 'zh' ? 'EC MOP 占用期限限制' : 'EC MOP Timeline', 
      desc: language === 'zh' ? '执行共管公寓 (EC) 自竣工交付起需满足5年的最低居住占用期(MOP)。' : '5-year Minimum Occupation Period applies from completion.', 
      status: language === 'zh' ? '活跃政策' : 'Active', 
      icon: <Calendar size={20} /> 
    },
    { 
      title: language === 'zh' ? '首套房买家配额比例' : 'First-Timer Quota', 
      desc: language === 'zh' ? '新推出楼盘中，多达 95% 的公共销售单位优先预留给首套购房者。' : '95% of public launch units reserved for first-timers.', 
      status: language === 'zh' ? '优先认购' : 'Priority', 
      icon: <Users size={20} /> 
    },
    { 
      title: language === 'zh' ? '付款方案与规则对比' : 'Payment Scheme', 
      desc: language === 'zh' ? '标准渐进付款方案 (NPS) 与推迟付款方案 (DPS) 的规范性条约对比。' : 'Normal vs Deferred Payment Schemes comparison.', 
      status: language === 'zh' ? '政策法规' : 'Regulation', 
      icon: <ShieldCheck size={20} /> 
    },
    { 
      title: language === 'zh' ? 'MOP 宽限截止变更' : 'MOP Deadline', 
      desc: language === 'zh' ? '政府有关居住期限锁定的关键调整与修正即将在2026年5月实施生效。' : 'Key changes coming in May 2026.', 
      status: language === 'zh' ? '即将推行' : 'Upcoming', 
      icon: <Zap size={20} /> 
    },
  ];

  const tableTitle = language === 'zh' ? '最新热门私宅转售成交记录' : 'Top Recent Resale Transactions';
  const csvButton = language === 'zh' ? '导出 CSV 数据' : 'Export CSV';
  const thLocation = language === 'zh' ? '成交楼盘 / 地段位置' : 'Location / Project';
  const thPrice = language === 'zh' ? '总成交价 (新币)' : 'Transacted Price';
  const thMonth = language === 'zh' ? '交易月份' : 'Month';
  const loadingText = language === 'zh' ? '正在加载最新实时房产交易记录...' : 'Loading live transaction data...';

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <h1>{t('nav.policy')}</h1>
      </header>

      <section className={styles.policyGrid}>
        {policies.map(policy => (
          <div key={policy.title} className={`card ${styles.policyCard}`}>
            <div className={styles.policyIcon}>{policy.icon}</div>
            <h3>{policy.title}</h3>
            <p>{policy.desc}</p>
            <span className={styles.statusBadge}>{policy.status}</span>
          </div>
        ))}
      </section>

      <div className={styles.benchmarkSection}>
        <div className={`card ${styles.tableCard}`}>
          <div className={styles.tableHeader}>
            <h3>{tableTitle}</h3>
            <button className={styles.exportBtn}>{csvButton}</button>
          </div>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>{thLocation}</th>
                <th>{thPrice}</th>
                <th>{thMonth}</th>
              </tr>
            </thead>
            <tbody>
              {topTrans.length > 0 ? topTrans.map((row, i) => (
                <tr key={i}>
                  <td className={styles.projectName}>{row.project}</td>
                  <td>${Number(row.price).toLocaleString()}</td>
                  <td>{row.date}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={3}>{loadingText}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
