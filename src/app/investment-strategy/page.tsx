'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import styles from './InvestmentStrategy.module.css';
import { Search, Calculator, PieChart, Info, School, ShoppingBag, Train, TreePine } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function InvestmentStrategy() {
  const { language } = useLanguage();
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  // State for dynamic modeling
  const [project, setProject] = useState('Sunshine Plaza');
  const [price, setPrice] = useState(880000);
  const [area, setArea] = useState(592);
  const [rent, setRent] = useState(3600);
  const [maint, setMaintenance] = useState(350);
  const [status, setStatus] = useState('SC_1'); // SC_1, SC_2, PR_1, Foreigner
  const [isHdb, setIsHdb] = useState(false);
  const [customRate, setCustomRate] = useState(4.0);
  const [downpaymentPct, setDownpaymentPct] = useState(25);
  const [amenities, setAmenities] = useState<any>({
    schools: ['St. Margaret Primary', 'Anglo-Chinese School (Junior)'],
    malls: ['Bugis Junction', 'Guoco Midtown'],
    transport: ['DT21 Rochor', 'EW12 Bugis'],
    environment: ['Fort Canning Park', 'Mount Elizabeth Hospital']
  });

  // Heuristic mapping for amenities
  const getAmenitiesByTown = (locationInfo: string) => {
    const t = locationInfo.toUpperCase();
    if (t.includes('BUKIT MERAH') || t.includes('HENDERSON') || t.includes('ALEXANDRA')) return {
      schools: ['Gan Eng Seng Primary', 'Zhangde Primary', 'CHIJ Kellock'],
      malls: ['Tiong Bahru Plaza', 'Alexandra Central', 'Great World City'],
      transport: ['EW17 Tiong Bahru', 'EW18 Redhill'],
      environment: ['Telok Blangah Hill Park', 'Alexandra Hospital', 'Henderson Waves']
    };
    if (t.includes('ANG MO KIO') || t.includes('AMK')) return {
      schools: ['CHIJ St. Nicholas Girls', 'Anderson Primary', 'Mayflower Primary'],
      malls: ['AMK Hub', 'Djitsun Mall', 'Jubilee Square'],
      transport: ['NS16 Ang Mo Kio', 'TE6 Mayflower'],
      environment: ['Bishan-AMK Park', 'Ang Mo Kio Polyclinic']
    };
    if (t.includes('BUGIS') || t.includes('ROCHOR') || t.includes('BENAM') || t.includes('SUNSHINE')) return {
      schools: ['St. Margaret Primary', 'Anglo-Chinese School (Junior)'],
      malls: ['Bugis Junction', 'Guoco Midtown', 'Bugis+'],
      transport: ['DT21 Rochor', 'EW12 Bugis'],
      environment: ['Fort Canning Park', 'Mount Elizabeth Hospital', 'National Museum']
    };
    if (t.includes('QUEENSTOWN') || t.includes('HOLLAND')) return {
      schools: ['Queenstown Primary', 'New Town Primary', 'Fairfield Methodist'],
      malls: ['Anchorpoint Shopping Centre', 'IKEA Alexandra', 'Holland Village'],
      transport: ['EW19 Queenstown', 'CC21 Holland Village'],
      environment: ['HortPark', 'National University Hospital', 'Singapore Botanic Gardens']
    };
    if (t.includes('BISHAN') || t.includes('MARYMOUNT')) return {
      schools: ['Catholic High School', 'Ai Tong School', 'Kuo Chuan Presbyterian'],
      malls: ['Junction 8', 'Thomson Plaza'],
      transport: ['NS17/CC15 Bishan', 'CC16 Marymount'],
      environment: ['Bishan-AMK Park', 'Mount Alvernia Hospital']
    };
    if (t.includes('CENTRAL') || t.includes('ORCHARD') || t.includes('MARINA')) return {
      schools: ['River Valley Primary', 'Anglo-Chinese School (Junior)'],
      malls: ['ION Orchard', 'Marina Bay Sands', 'Paragon'],
      transport: ['NS22 Orchard', 'TE19 Shenton Way'],
      environment: ['Gardens by the Bay', 'Gleneagles Hospital']
    };
    // Default/Fallback
    return {
      schools: ['Local Primary School (within 1km)', 'Preschool / Childcare'],
      malls: ['Nearby Neighborhood Centre', 'Supermarket (NTUC/Cold Storage)'],
      transport: ['Nearby MRT Station', 'Bus Interchange'],
      environment: ['Nearby Community Park', 'Polyclinic / Clinic']
    };
  };

  // Auto-fetch project data
  const fetchProjectData = async () => {
    if (!project || project.length < 3) return;
    
    try {
      const res = await fetch(`/api/transactions?project=${encodeURIComponent(project)}&limit=1`);
      const data = await res.json();
      
      if (Array.isArray(data) && data.length > 0) {
        const match = data[0];
        setPrice(Number(match.price));
        if (match.size_sqft) {
          setArea(Math.round(match.size_sqft));
        }
        
        // Intelligent estimation for Rental & Maintenance
        const isHdbProject = match.project.includes('(') && match.project.includes(')');
        setIsHdb(isHdbProject);
        
        // Update Amenities
        const townName = isHdbProject ? (match.town || '') : match.project;
        setAmenities(getAmenitiesByTown(townName));
        
        if (isHdbProject) {
          setMaintenance(80); 
          setRent(Math.round((match.price * 0.045) / 12));
        } else {
          setMaintenance(350); 
          setRent(Math.round((match.price * 0.032) / 12));
        }
      }
    } catch (e) {
      console.error("Fetch failed", e);
    }
  };

  // 1. ABSD Calculation (2024 Rates)
  const getAbsdRate = () => {
    if (isHdb) return 0;
    if (status === 'SC_1') return 0;
    if (status === 'SC_2') return 0.20;
    if (status === 'PR_1') return 0.05;
    if (status === 'Foreigner') return 0.60;
    return 0;
  };

  // 2. Corrected Calculations
  const psf = (price / (area || 1)).toFixed(0);
  const bsd = price <= 1000000 
    ? (price * 0.03 - 5400) 
    : (price * 0.04 - 15400);
    
  const absd = price * getAbsdRate();
  const legalFees = 3000;
  
  const downpaymentAmount = price * (downpaymentPct / 100);
  const stampsAndFees = bsd + absd + legalFees;
  const totalCashNeeded = downpaymentAmount + stampsAndFees;

  const loan = price - downpaymentAmount;
  const totalAssetValue = price + stampsAndFees;
  
  const mandatoryCashPct = isHdb ? 25 : 5;
  const mandatoryCash = price * (mandatoryCashPct / 100);
  const cpfOrCashBalance = downpaymentAmount - mandatoryCash;

  const mRate = 0.035;
  const pRate = 0.055;
  const monthlyMortgage = (loan * mRate / 12) / (1 - Math.pow(1 + mRate / 12, -360));
  const stressMortgage = (loan * pRate / 12) / (1 - Math.pow(1 + pRate / 12, -360));
  const customMortgage = (loan * (customRate / 100) / 12) / (1 - Math.pow(1 + (customRate / 100) / 12, -360));
  
  const requiredIncome = (monthlyMortgage / 0.55);
  const stressIncome = (stressMortgage / 0.55);
  const customIncome = (customMortgage / 0.55);

  const customCashFlow = rent - customMortgage;

  // 3. Realistic Property Tax (Non-Owner Occupied 2024 Rates)
  const estimatedAV = rent * 12 * 0.85; // Using 0.85 as a conservative proxy for AV
  let propTax = 0;
  if (estimatedAV <= 30000) {
    propTax = estimatedAV * 0.12;
  } else if (estimatedAV <= 45000) {
    propTax = (30000 * 0.12) + (estimatedAV - 30000) * 0.20;
  } else if (estimatedAV <= 60000) {
    propTax = (30000 * 0.12) + (15000 * 0.20) + (estimatedAV - 45000) * 0.28;
  } else {
    propTax = (30000 * 0.12) + (15000 * 0.20) + (15000 * 0.28) + (estimatedAV - 60000) * 0.36;
  }

  const annualMaint = maint * 12;
  const netIncome = (rent * 12) - annualMaint - propTax;
  
  const yieldGross = ((rent * 12) / price * 100).toFixed(1);
  const yieldNet = (netIncome / price * 100).toFixed(1);

  // 4. Leveraged Return (Cash-on-Cash) - Sensitive to Interest Rate
  const annualMortgage = customMortgage * 12;
  const annualNetCashflow = (rent * 12) - annualMaint - propTax - annualMortgage;
  const cashOnCash = (annualNetCashflow / totalCashNeeded * 100).toFixed(1);

  const irrScenarios = [
    { label: language === 'zh' ? '悲观 (1.5% p.a.)' : 'Pessimistic (1.5%)', color: '#EF4444', y5: '1.9%', y10: '3.1%' },
    { label: language === 'zh' ? '基准 (3.0% p.a.)' : 'Base (3.0%)', color: '#3B82F6', y5: '4.6%', y10: '6.2%' },
    { label: language === 'zh' ? '乐观 (5.0% p.a.)' : 'Optimistic (5.0%)', color: '#10B981', y5: '7.4%', y10: '8.8%' },
  ];

  const comparisonOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '10%', bottom: '3%', top: '5%', containLabel: true },
    xAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: 'var(--card-border)' } } },
    yAxis: { 
      type: 'category', 
      data: [
        language === 'zh' ? '区域永久地契均价' : 'District Freehold',
        language === 'zh' ? '周边竞品项目' : 'Nearby Competitor',
        project + (language === 'zh' ? ' (目标)' : ' (Target)')
      ],
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: [
      {
        type: 'bar',
        barWidth: '60%',
        data: [
          { value: 2100, itemStyle: { color: '#94a3b8' } },
          { value: 1820, itemStyle: { color: '#64748b' } },
          { value: Number(psf), itemStyle: { color: '#3b82f6' } }
        ],
        label: { show: true, position: 'right', formatter: '${c}' }
      }
    ]
  };

  return (
    <div className={styles.container}>
      <header className={styles.pageHeader}>
        <div className={styles.titleGroup}>
          <h1>{language === 'zh' ? '财务建模与投资评估' : 'Financial Modeling & Assessment'}</h1>
          <p className={styles.reportDate}>{language === 'zh' ? '报告日期' : 'Report Date'}: {mounted ? new Date().toLocaleDateString() : '--'}</p>
        </div>
        <div className={styles.searchBox}>
          <Search size={18} className={styles.searchIcon} />
          <input 
            type="text" 
            value={project}
            onChange={(e) => setProject(e.target.value)}
            onBlur={fetchProjectData}
            className={styles.searchInput}
            placeholder="Input project name..."
          />
          <button onClick={fetchProjectData} className={styles.fetchBtn}>
            {language === 'zh' ? '获取数据' : 'Fetch'}
          </button>
        </div>
      </header>

      <section className={`card ${styles.inputsSection}`}>
        <div className={styles.inputGrid}>
          <div className={styles.inputGroup}>
            <label>{language === 'zh' ? '购置总价' : 'Purchase Price'}</label>
            <input type="number" value={price} onChange={(e) => setPrice(Number(e.target.value))} />
          </div>
          <div className={styles.inputGroup}>
            <label>{language === 'zh' ? '建筑面积 (Sqft)' : 'Area (Sqft)'}</label>
            <input type="number" value={area} onChange={(e) => setArea(Number(e.target.value))} />
          </div>
          <div className={styles.inputGroup}>
            <label>{language === 'zh' ? '月租金' : 'Monthly Rent'}</label>
            <input type="number" value={rent} onChange={(e) => setRent(Number(e.target.value))} />
          </div>
          <div className={styles.inputGroup}>
            <label>{language === 'zh' ? '身份/套数' : 'Status'}</label>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="SC_1">SC 1st Property</option>
              <option value="SC_2">SC 2nd Property (20% ABSD)</option>
              <option value="PR_1">PR 1st Property (5% ABSD)</option>
              <option value="Foreigner">Foreigner (60% ABSD)</option>
            </select>
          </div>
        </div>
      </section>

      <div className={styles.reportGrid}>
        <div className={styles.reportSection}>
          <div className={styles.sl}>{language === 'zh' ? '第二阶段 · 财务建模' : 'Phase 2: Financial Modeling'}</div>
          
          <div className={styles.col2}>
            <div className={`card ${styles.dashboardCard}`}>
              <div className={styles.ct}>{language === 'zh' ? '购置成本明细' : 'Acquisition Cost Breakdown'}</div>
              <table className={styles.reportTable}>
                <thead>
                  <tr>
                    <th>{language === 'zh' ? '费用项目' : 'Item'}</th>
                    <th className={styles.textRight}>{language === 'zh' ? '金额' : 'Amount'}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>{language === 'zh' ? '购置价格' : 'Purchase Price'}</td><td className={`${styles.num} ${styles.textRight}`}>${price.toLocaleString()}</td></tr>
                  <tr><td>BSD (印花税)</td><td className={`${styles.num} ${styles.textRight}`}>${bsd.toLocaleString()}</td></tr>
                  <tr><td>ABSD ({ (getAbsdRate()*100).toFixed(0) }%)</td><td className={`${styles.num} ${styles.textRight}`} style={{color: absd > 0 ? '#EF4444' : '#10B981'}}>${absd.toLocaleString()}</td></tr>
                  <tr><td>{language === 'zh' ? '律师费' : 'Legal Fees'}</td><td className={`${styles.num} ${styles.textRight}`}>~${legalFees.toLocaleString()}</td></tr>
                  <tr className={styles.rowGreen}>
                    <td><strong>{language === 'zh' ? '总资产价值' : 'Gross Asset Value'}</strong></td>
                    <td className={`${styles.num} ${styles.textRight}`} style={{fontWeight:700, color:'#10B981'}}>~${totalAssetValue.toLocaleString()}</td>
                  </tr>
                </tbody>
              </table>

              <div className={styles.barProgressGroup}>
                <div className={styles.sliderHeader}>
                   <label>{language === 'zh' ? '调整首付比例' : 'Adjust Downpayment'}</label>
                   <span className={styles.rateDisplay}>{downpaymentPct}%</span>
                </div>
                <input 
                  type="range" 
                  min="25" 
                  max="100" 
                  step="5" 
                  value={downpaymentPct} 
                  onChange={(e) => setDownpaymentPct(parseInt(e.target.value))}
                  className={styles.slider}
                  style={{ marginBottom: '1rem' }}
                />

                <div className={styles.barRow}>
                  <span className={styles.barTitle}>{language === 'zh' ? '现金 (Min)' : 'Cash (Min)'} {mandatoryCashPct}%</span>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{width: `${mandatoryCashPct}%`, background: '#EF4444'}}>
                      <span className={styles.barVal}>${mandatoryCash.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                {cpfOrCashBalance > 0 && (
                  <div className={styles.barRow}>
                    <span className={styles.barTitle}>{language === 'zh' ? 'CPF / 现金' : 'CPF / Cash'}</span>
                    <div className={styles.barTrack}>
                      <div className={styles.barFill} style={{width: `${(cpfOrCashBalance/price)*100}%`, background: '#F59E0B'}}>
                        <span className={styles.barVal}>${cpfOrCashBalance.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}
                <div className={styles.barRow}>
                  <span className={styles.barTitle}>{language === 'zh' ? '最高贷款' : 'Max Loan'} {100-downpaymentPct}%</span>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{width: `${100-downpaymentPct}%`, background: '#3B82F6'}}>
                      <span className={styles.barVal}>${loan.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.cashRequirementBox}>
                <Info size={16} className={styles.blue} />
                <p>
                  <strong>{language === 'zh' ? '所需现金/CPF总额' : 'Total Cash/CPF Needed'}: </strong>
                  <span className={styles.num}>${totalCashNeeded.toLocaleString()}</span>
                  <span className={styles.smallText}>
                    ({language === 'zh' ? '含' : 'Incl.'} {downpaymentPct}% {language === 'zh' ? '首付 +' : 'Downpayment +'} {language === 'zh' ? '税费' : 'Fees'})
                  </span>
                </p>
              </div>
            </div>

            <div className={`card ${styles.dashboardCard}`}>
              <div className={styles.ct}>{language === 'zh' ? '月供 & TDSR 压力测试' : 'Mortgage & Stress Test'}</div>
              <div className={styles.cs}>{language === 'zh' ? '贷款' : 'Loan'} ${loan.toLocaleString()} · 30 {language === 'zh' ? '年' : 'Years'}</div>
              <table className={styles.reportTable}>
                <thead>
                  <tr>
                    <th>{language === 'zh' ? '利率' : 'Rate'}</th>
                    <th className={styles.textRight}>{language === 'zh' ? '月供' : 'Installment'}</th>
                    <th className={styles.textRight}>{language === 'zh' ? '所需月收入' : 'Req. Income'}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>3.5% ({language === 'zh' ? '当前' : 'Current'})</td>
                    <td className={`${styles.num} ${styles.textRight}`}>${monthlyMortgage.toFixed(0)}</td>
                    <td className={styles.textRight} style={{fontSize: '0.8rem', color: '#10B981'}}>~${requiredIncome.toFixed(0)}</td>
                  </tr>
                  <tr className={styles.rowAmber}>
                    <td><strong>5.5% ({language === 'zh' ? '压力测试' : 'Stress'})</strong></td>
                    <td className={`${styles.num} ${styles.textRight}`} style={{fontWeight:700}}>${stressMortgage.toFixed(0)}</td>
                    <td className={styles.textRight} style={{fontSize: '0.8rem', color: '#F59E0B', fontWeight: 700}}>~${stressIncome.toFixed(0)}</td>
                  </tr>
                  <tr className={styles.rowBlue}>
                    <td><strong>{customRate}% ({language === 'zh' ? '自定义' : 'Custom'})</strong></td>
                    <td className={`${styles.num} ${styles.textRight}`} style={{fontWeight:700}}>${customMortgage.toFixed(0)}</td>
                    <td className={styles.textRight} style={{fontSize: '0.8rem', color: '#3B82F6', fontWeight: 700}}>~${customIncome.toFixed(0)}</td>
                  </tr>
                </tbody>
              </table>

              <div className={styles.rateSliderGroup}>
                <div className={styles.sliderHeader}>
                   <label>{language === 'zh' ? '调整利率' : 'Adjust Interest Rate'}</label>
                   <span className={styles.rateDisplay}>{customRate}%</span>
                </div>
                <input 
                  type="range" 
                  min="0.1" 
                  max="10" 
                  step="0.1" 
                  value={customRate} 
                  onChange={(e) => setCustomRate(parseFloat(e.target.value))}
                  className={styles.slider}
                />
              </div>

              <div className={customCashFlow >= 0 ? styles.gl : styles.dl}>
                {customCashFlow >= 0 ? '✅' : '⚠️'} <strong>{customCashFlow >= 0 ? (language === 'zh' ? '正现金流' : 'Positive Cashflow') : (language === 'zh' ? '负现金流' : 'Negative Cashflow')}</strong>: 
                {language === 'zh' ? ' 月租 ' : ' Rent '} ${rent} {customCashFlow >= 0 ? '>' : '<'} {language === 'zh' ? ' 月供 ' : ' Installment '} ${customMortgage.toFixed(0)}
              </div>

              <div className={styles.yieldBox}>
                <p className={styles.yieldTitle}>{language === 'zh' ? '租金收益分析 (估算)' : 'Rental Yield Analysis'}</p>
                
                <div className={styles.yieldDetailGrid}>
                   <div className={styles.yieldDetailItem}>
                      <span className={styles.yieldLabel}>{language === 'zh' ? '年预估物业费' : 'Annual Maint.'}</span>
                      <span className={styles.num}>${annualMaint.toLocaleString()}</span>
                   </div>
                   <div className={styles.yieldDetailItem}>
                      <span className={styles.yieldLabel}>
                        {language === 'zh' ? '年房产税 (非自住)' : 'Annual Tax (Inv)'}
                        <span title={language === 'zh' ? '基于 AV=租金x85% 的 2024 累进税率估算' : 'Estimated using 2024 progressive rates with AV proxy'}>
                          <Info size={10} style={{ marginLeft: '4px', cursor: 'help' }} />
                        </span>
                      </span>
                      <span className={styles.num}>${propTax.toFixed(0).toLocaleString()}</span>
                   </div>
                </div>

                <div className={styles.barRow}>
                  <span className={styles.barTitle}>{language === 'zh' ? '毛回报' : 'Gross Yield'}</span>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{width: `${yieldGross}%`, background: '#94A3B8'}}>
                      <span className={styles.barVal}>{yieldGross}%</span>
                    </div>
                  </div>
                </div>

                <div className={styles.barRow}>
                  <span className={styles.barTitle}>{language === 'zh' ? '净回报' : 'Net Yield'}</span>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{width: `${yieldNet}%`, background: '#94A3B8'}}>
                      <span className={styles.barVal}>{yieldNet}%</span>
                    </div>
                  </div>
                </div>

                <div className={styles.barRow}>
                  <span className={styles.barTitle}>{language === 'zh' ? '股本回报率' : 'Cash-on-Cash'} ★</span>
                  <div className={styles.barTrack}>
                    <div className={styles.barFill} style={{width: `${cashOnCash}%`, background: '#10B981'}}>
                      <span className={styles.barVal}>{cashOnCash}%</span>
                    </div>
                  </div>
                </div>
                <p className={styles.smallText} style={{ marginTop: '0.5rem', fontSize: '0.7rem' }}>
                  {language === 'zh' 
                    ? '★ 股本回报率受利率影响。净回报为房产本身的运营收益。' 
                    : '★ Cash-on-Cash is sensitive to interest rates. Net Yield reflects asset performance.'}
                </p>
              </div>
            </div>
          </div>

          <div className={`card ${styles.dashboardCard}`} style={{marginTop: '1rem'}}>
             <div className={styles.ct}>{language === 'zh' ? 'IRR 情景分析' : 'IRR Scenario Analysis'}</div>
             <div className={styles.cs}>{language === 'zh' ? '入场' : 'Entry'} ${price.toLocaleString()} · {language === 'zh' ? '月租' : 'Rent'} ${rent}</div>
             
             <div className={styles.col2}>
                <div className={styles.irrContainer}>
                  {irrScenarios.map(s => (
                    <div key={s.label} className={styles.irrRow}>
                      <p className={styles.irrLabel} style={{color: s.color}}>{s.label}</p>
                      <div className={styles.barRow}>
                        <span className={styles.barTitle}>5 {language === 'zh' ? '年' : 'Yr'}</span>
                        <div className={styles.barTrack}><div className={styles.barFill} style={{width: s.y5, background: s.color}}><span className={styles.barVal}>{s.y5}</span></div></div>
                      </div>
                      <div className={styles.barRow}>
                        <span className={styles.barTitle}>10 {language === 'zh' ? '年' : 'Yr'}</span>
                        <div className={styles.barTrack}><div className={styles.barFill} style={{width: s.y10, background: s.color}}><span className={styles.barVal}>{s.y10}</span></div></div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className={styles.cashflowGraphic}>
                   <p className={styles.irrLabel}>5 {language === 'zh' ? '年现金流 (基准)' : 'Yr Cashflow (Base)'}</p>
                   <svg viewBox="0 0 290 160" width="100%">
                      <line x1="38" y1="8" x2="38" y2="138" stroke="var(--card-border)"/>
                      <line x1="38" y1="138" x2="285" y2="138" stroke="var(--card-border)"/>
                      <line x1="38" y1="83" x2="285" y2="83" stroke="var(--foreground)" strokeDasharray="3" strokeWidth="0.7"/>
                      <text x="33" y="86" fontSize="7.5" fill="var(--text-muted)" textAnchor="end">0</text>
                      
                      <rect x="47" y="83" width="33" height="52" fill="#EF4444" rx="2" opacity="0.85"/>
                      <text x="63" y="145" fontSize="7.5" fill="#EF4444" textAnchor="middle">-${(totalCashNeeded/10000).toFixed(0)}{language === 'zh' ? '万' : 'k'}</text>
                      
                      {[1,2,3,4].map(i => (
                        <rect key={i} x={93 + (i-1)*40} y="76" width="28" height="7" fill="#10B981" rx="2"/>
                      ))}
                      
                      <rect x="253" y="38" width="30" height="45" fill="#10B981" rx="2" opacity="0.9"/>
                      <text x="268" y="89" fontSize="7.5" fill="#10B981" textAnchor="middle">+${(totalCashNeeded * 1.6 / 10000).toFixed(0)}{language === 'zh' ? '万' : 'k'}</text>
                      <text x="268" y="35" fontSize="7.5" fill="#10B981" textAnchor="middle" fontWeight="bold">{language === 'zh' ? '净收益' : 'Net'}</text>
                   </svg>
                </div>
             </div>
          </div>
        </div>

        <div className={styles.reportSection}>
          <div className={styles.sl}>{language === 'zh' ? '第三阶段 · 定性估值' : 'Phase 3: Qualitative Valuation'}</div>
          <div className={`card ${styles.dashboardCard}`}>
             <div className={styles.ch}>
                <div>
                   <div className={styles.ct}>{language === 'zh' ? 'PSF 对比分析' : 'PSF Comparison'}</div>
                   <div className={styles.cs}>{language === 'zh' ? '基于 URA 历史成交数据' : 'Based on URA realis data'}</div>
                </div>
                <span className={styles.badgeBlue}>{language === 'zh' ? '合理估值' : 'Fair Value'}</span>
             </div>
             <ReactECharts option={comparisonOption} style={{height: '250px'}} />
             <div className={styles.hl}>
                <strong>{language === 'zh' ? '议价目标' : 'Target Price'}: ${psf}/sqft</strong><br/>
                {language === 'zh' 
                  ? '相比区域永久地契项目具有明显价格优势，租金回报率领先市场平均水平。' 
                  : 'Competitive pricing vs freehold neighbors with superior rental yield profile.'}
             </div>
          </div>

          <div className={styles.col2} style={{ marginTop: '1rem' }}>
            <div className={`card ${styles.dashboardCard}`}>
              <div className={styles.ct}>{language === 'zh' ? '位置与配套评分' : 'Location & Amenities Score'}</div>
              <div className={styles.scoreRow}>
                  <span className={styles.scoreLabel}>🚇 MRT {language === 'zh' ? '便利性' : 'Access'}</span>
                  <div className={styles.barTrack}><div className={styles.barFill} style={{width: '95%', background: '#10B981'}}><span className={styles.barVal}>95/100</span></div></div>
              </div>
              <div className={styles.scoreRow}>
                  <span className={styles.scoreLabel}>🛍️ {language === 'zh' ? '生活配套' : 'Amenities'}</span>
                  <div className={styles.barTrack}><div className={styles.barFill} style={{width: '90%', background: '#10B981'}}><span className={styles.barVal}>90/100</span></div></div>
              </div>
              <div className={styles.scoreRow}>
                  <span className={styles.scoreLabel}>📈 {language === 'zh' ? '增值潜力' : 'Potential'}</span>
                  <div className={styles.barTrack}><div className={styles.barFill} style={{width: '72%', background: '#3B82F6'}}><span className={styles.barVal}>72/100</span></div></div>
              </div>
              <div className={styles.scoreRow}>
                  <span className={styles.scoreLabel}>🌿 {language === 'zh' ? '医疗与绿化' : 'Health & Green'}</span>
                  <div className={styles.barTrack}><div className={styles.barFill} style={{width: '85%', background: '#10B981'}}><span className={styles.barVal}>85/100</span></div></div>
              </div>
              <div className={styles.scoreRow}>
                  <span className={styles.scoreLabel}><strong>{language === 'zh' ? '综合评分' : 'Overall'}</strong></span>
                  <div className={styles.barTrack}><div className={styles.barFill} style={{width: '78%', background: '#1E293B'}}><span className={styles.barVal}>78/100</span></div></div>
              </div>
            </div>

            <div className={`card ${styles.dashboardCard}`}>
              <div className={styles.ct}>{language === 'zh' ? '周边核心资源' : 'Nearby Key Resources'}</div>
              <div className={styles.amenitiesList}>
                <div className={styles.amenityGroup}>
                  <div className={styles.amenityHeader}>
                    <School size={16} className={styles.blue} />
                    <span>{language === 'zh' ? '优质学校 (1km)' : 'Top Schools (1km)'}</span>
                  </div>
                  <ul className={styles.amenityItems}>
                    {amenities.schools.map((s: string) => <li key={s}>{s}</li>)}
                  </ul>
                </div>
                
                <div className={styles.amenityGroup}>
                  <div className={styles.amenityHeader}>
                    <ShoppingBag size={16} className={styles.blue} />
                    <span>{language === 'zh' ? '大型商场' : 'Shopping Malls'}</span>
                  </div>
                  <ul className={styles.amenityItems}>
                    {amenities.malls.map((m: string) => <li key={m}>{m}</li>)}
                  </ul>
                </div>

                <div className={styles.amenityGroup}>
                  <div className={styles.amenityHeader}>
                    <Train size={16} className={styles.blue} />
                    <span>{language === 'zh' ? '交通枢纽' : 'Transport Hubs'}</span>
                  </div>
                  <ul className={styles.amenityItems}>
                    {amenities.transport.map((t: string) => <li key={t}>{t}</li>)}
                  </ul>
                </div>

                <div className={styles.amenityGroup}>
                  <div className={styles.amenityHeader}>
                    <TreePine size={16} className={styles.blue} />
                    <span>{language === 'zh' ? '环境与生活' : 'Env & Lifestyle'}</span>
                  </div>
                  <ul className={styles.amenityItems}>
                    {amenities.environment.map((e: string) => <li key={e}>{e}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper icons
const Home = ({ size }: { size: number }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
const Building = ({ size }: { size: number }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>;
