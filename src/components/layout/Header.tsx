'use client';

import { useLanguage } from '@/context/LanguageContext';
import { Globe, Bell, User, Search } from 'lucide-react';
import styles from './Header.module.css';

const Header = () => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className={styles.header}>
      <div className={styles.search}>
        <Search size={18} className={styles.searchIcon} />
        <input type="text" placeholder="Search property data..." />
      </div>

      <div className={styles.actions}>
        <button 
          className={styles.langSwitch}
          onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
        >
          <Globe size={18} />
          <span>{language === 'en' ? '中文' : 'English'}</span>
        </button>

        <button className={styles.iconBtn}>
          <Bell size={18} />
          <span className={styles.badge}></span>
        </button>

        <div className={styles.userProfile}>
          <div className={styles.avatar}>
            <User size={20} />
          </div>
          <div className={styles.userInfo}>
            <span className={styles.userName}>Admin</span>
            <span className={styles.userRole}>Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
