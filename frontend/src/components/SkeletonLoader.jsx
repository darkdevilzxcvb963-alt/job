export default function SkeletonLoader({ type = 'card', count = 3 }) {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className="skeleton-card">
            <div className="skeleton-line skeleton-title"></div>
            <div className="skeleton-line skeleton-subtitle"></div>
            <div className="skeleton-line skeleton-text"></div>
            <div className="skeleton-line skeleton-text short"></div>
          </div>
        )
      case 'list':
        return (
          <div className="skeleton-list-item">
            <div className="skeleton-avatar"></div>
            <div className="skeleton-list-content">
              <div className="skeleton-line skeleton-title"></div>
              <div className="skeleton-line skeleton-text"></div>
            </div>
          </div>
        )
      case 'chart':
        return (
          <div className="skeleton-chart">
            <div className="skeleton-line skeleton-title"></div>
            <div className="skeleton-chart-bars">
              {[40, 65, 85, 55, 70].map((h, i) => (
                <div key={i} className="skeleton-bar" style={{ height: `${h}%` }}></div>
              ))}
            </div>
          </div>
        )
      default:
        return <div className="skeleton-card"><div className="skeleton-line"></div></div>
    }
  }

  return (
    <div className="skeleton-container">
      {Array.from({ length: count }, (_, i) => (
        <div key={i}>{renderSkeleton()}</div>
      ))}
    </div>
  )
}
