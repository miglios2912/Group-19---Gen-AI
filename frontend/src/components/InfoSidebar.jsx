import React from 'react';
import './InfoSidebar.css'; // We will create this file next

// A list of useful links and information
const usefulLinks = [
  {
    title: "TUMonline Portal",
    description: "Your main campus management system.",
    url: "https://campus.tum.de/"
  },
  {
    title: "University Library",
    description: "Find books, articles, and research papers.",
    url: "https://www.ub.tum.de/"
  },
  {
    title: "IT Service Desk",
    description: "Help with accounts, software, and IT issues.",
    url: "https://www.it.tum.de/it-support/"
  },
  {
    title: "Moodle Learning Platform",
    description: "Access your course materials and forums.",
    url: "https://www.moodle.tum.de/"
  }
];

export default function InfoSidebar() {
  return (
    <aside className="info-sidebar">
      <h2 className="sidebar-title">Useful Information</h2>
      <div className="info-cards-container">
        {usefulLinks.map((link, index) => (
          <a key={index} href={link.url} target="_blank" rel="noopener noreferrer" className="info-card">
            <h3>{link.title}</h3>
            <p>{link.description}</p>
          </a>
        ))}
      </div>
    </aside>
  );
}