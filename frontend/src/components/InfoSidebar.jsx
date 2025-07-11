import React, { useState } from 'react';
import './InfoSidebar.css';
import DarkModeToggle from './DarkModeToggle.jsx';

// Campus data for interactive maps
const campusData = {
  munich: {
    name: "Munich Campus",
    image: "/images/campus-maps/munich.png",
    description: "Main campus in downtown Munich"
  },
  garching: {
    name: "Garching Campus", 
    image: "/images/campus-maps/garching.png",
    description: "Research campus for engineering and natural sciences"
  },
  weihenstephan: {
    name: "Weihenstephan Campus",
    image: "/images/campus-maps/weihenstephan.png", 
    description: "Campus for life sciences and food technology"
  },
  heilbronn: {
    name: "Heilbronn Campus",
    url: "https://bildungscampus.hn/#open-locations",
    description: "Bildungscampus for management and technology"
  }
};

// A list of useful links and information
const usefulLinks = [
  {
    title: "TUMonline Portal",
    description: "Your main campus management system.",
    url: "https://campus.tum.de/",
    icon: "🏫"
  },
  {
    title: "University Library",
    description: "Find books, articles, and research papers.",
    url: "https://www.ub.tum.de/",
    icon: "📚"
  },
  {
    title: "IT Service Desk",
    description: "Help with accounts, software, and IT issues.",
    url: "https://www.it.tum.de/it-support/",
    icon: "💻"
  },
  {
    title: "Moodle Learning Platform",
    description: "Access your course materials and forums.",
    url: "https://www.moodle.tum.de/",
    icon: "🎓"
  },
  {
    title: "Student Services",
    description: "Registration, certificates, and administrative help.",
    url: "https://www.tum.de/en/studies/application-and-acceptance",
    icon: "📋"
  },
  {
    title: "Campus Map",
    description: "Find buildings and navigate the campus.",
    url: null, // Will be handled specially
    icon: "🗺️",
    special: "campus-map"
  }
];

const quickActions = [
  {
    title: "Email Setup",
    action: "How do I set up my TUM email?",
    icon: "📧"
  },
  {
    title: "WiFi Connection",
    action: "How do I connect to eduroam?",
    icon: "📶"
  },
  {
    title: "Student ID",
    action: "How do I upload my student ID photo?",
    icon: "🆔"
  },
  {
    title: "Campus Food",
    action: "Where can I eat on campus?",
    icon: "🍽️"
  }
];

export default function InfoSidebar({ isOpen, onClose, onQuickAction }) {
  const [showCampusMap, setShowCampusMap] = useState(false);
  const [selectedCampus, setSelectedCampus] = useState(null);

  const handleQuickAction = (action) => {
    if (onQuickAction) {
      onQuickAction(action);
    }
    onClose();
  };

  const handleCampusMapClick = (e) => {
    e.preventDefault();
    setShowCampusMap(true);
  };

  const handleCampusSelect = (campus) => {
    if (campusData[campus].url) {
      // For Heilbronn, open external link
      window.open(campusData[campus].url, '_blank');
      setShowCampusMap(false);
    } else {
      // For other campuses, show image modal
      setSelectedCampus(campus);
      setShowCampusMap(false);
    }
  };

  const closeCampusMap = () => {
    setShowCampusMap(false);
    setSelectedCampus(null);
  };

  return (
    <>
      <aside className={`info-sidebar-mobile ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo-container">
            <img src="/tum-logo.png" alt="TUM Logo" className="sidebar-logo" />
            <img src="/tum-logo.png" alt="TUM Logo" className="sidebar-logo-mobile-hidden" />
            <div className="sidebar-dark-mode-toggle">
              <DarkModeToggle />
            </div>
          </div>
          <button 
            className="close-button"
            onClick={onClose}
            aria-label="Close sidebar"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="sidebar-content">

          {/* Useful Links Section */}
          <section className="sidebar-section">
            <h3 className="section-title">Useful Links</h3>
            <div className="info-cards-mobile">
              {usefulLinks.map((link, index) => (
                link.special === "campus-map" ? (
                  <div 
                    key={index} 
                    className="info-card-mobile clickable"
                    onClick={handleCampusMapClick}
                  >
                    <div className="card-header">
                      <span className="card-icon">{link.icon}</span>
                      <h4 className="card-title">{link.title}</h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M7 17l9.2-9.2M17 17V7H7"/>
                      </svg>
                    </div>
                    <p className="card-description">{link.description}</p>
                  </div>
                ) : (
                  <a 
                    key={index} 
                    href={link.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="info-card-mobile"
                  >
                    <div className="card-header">
                      <span className="card-icon">{link.icon}</span>
                      <h4 className="card-title">{link.title}</h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M7 17l9.2-9.2M17 17V7H7"/>
                      </svg>
                    </div>
                    <p className="card-description">{link.description}</p>
                  </a>
                )
              ))}
            </div>
          </section>

          {/* Contact Section */}
          <section className="sidebar-section">
            <h3 className="section-title">Need More Help?</h3>
            <div className="contact-info">
              <a 
                href="mailto:onboarding-support@tum.de" 
                className="contact-button"
              >
                <span className="contact-icon">📧</span>
                <div className="contact-text">
                  <span className="contact-title">Ask for Help</span>
                  <span className="contact-subtitle">onboarding-support@tum.de</span>
                </div>
              </a>
              <a 
                href="https://forms.gle/FCaroo4Wc5EeCShC6"
                target="_blank"
                rel="noopener noreferrer"
                className="contact-button"
              >
                <span className="contact-icon">💡</span>
                <div className="contact-text">
                  <span className="contact-title">Suggest Improvement</span>
                  <span className="contact-subtitle">Help us improve</span>
                </div>
              </a>
            </div>
          </section>
        </div>
      </aside>

      {/* Campus Map Selection Modal */}
      {showCampusMap && (
        <div className="campus-modal-overlay" onClick={closeCampusMap}>
          <div className="campus-modal" onClick={e => e.stopPropagation()}>
            <div className="campus-modal-header">
              <h3>Select Campus Map</h3>
              <button className="close-button" onClick={closeCampusMap}>×</button>
            </div>
            <div className="campus-options">
              {Object.entries(campusData).map(([key, campus]) => (
                <div 
                  key={key}
                  className="campus-option"
                  onClick={() => handleCampusSelect(key)}
                >
                  <div className="campus-option-content">
                    <h4>{campus.name}</h4>
                    <p>{campus.description}</p>
                  </div>
                  <span className="campus-arrow">→</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Individual Campus Map Modal */}
      {selectedCampus && (
        <div className="campus-modal-overlay" onClick={closeCampusMap}>
          <div className="campus-map-modal" onClick={e => e.stopPropagation()}>
            <div className="campus-modal-header">
              <h3>{campusData[selectedCampus].name}</h3>
              <button className="close-button" onClick={closeCampusMap}>×</button>
            </div>
            <div className="campus-map-content">
              <img 
                src={campusData[selectedCampus].image}
                alt={`${campusData[selectedCampus].name} Map`}
                className="campus-map-image"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}