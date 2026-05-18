'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLanguage } from '@/context/LanguageContext';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Map, 
  Briefcase, 
  FileText,
  Building2,
  Globe
} from 'lucide-react';
import styles from './Sidebar.module.css';

const Sidebar = () => {
  const pathname = usePathname();
  const { t } = useLanguage();

  const navItems = [
    { name: t('nav.dashboard'), path: '/', icon: <LayoutDashboard size={20} /> },
    { name: t('nav.marketTrends'), path: '/market-trends', icon: <TrendingUp size={20} /> },
    { name: t('nav.landIntelligence'), path: '/land-intelligence', icon: <Map size={20} /> },
    { name: t('nav.macroAnalysis'), path: '/macro-analysis', icon: <Globe size={20} /> },
    { name: t('nav.investment'), path: '/investment-strategy', icon: <Briefcase size={20} /> },
    { name: t('nav.policy'), path: '/policy-benchmarks', icon: <FileText size={20} /> },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <Building2 className={styles.logoIcon} />
        <span>PropIntel</span>
      </div>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link 
            key={item.path} 
            href={item.path}
            className={`${styles.navItem} ${pathname === item.path ? styles.active : ''}`}
          >
            {item.icon}
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
