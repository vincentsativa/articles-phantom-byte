/**
 * Article Card Click Handler
 * Makes entire article card clickable, not just the title link
 */
document.addEventListener('DOMContentLoaded', function() {
    const articleCards = document.querySelectorAll('.article-card');
    
    articleCards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            // Find the link within this card
            const link = this.querySelector('.card-title a');
            
            if (link && link.href) {
                // Check if it's an external link
                const isExternal = link.target === '_blank';
                
                // Don't trigger if clicking on a link that's already handled (like social buttons in future)
                if (e.target.tagName === 'A' && e.target.href === link.href) {
                    return;
                }
                
                // Navigate to the article
                if (isExternal) {
                    window.open(link.href, '_blank');
                } else {
                    window.location.href = link.href;
                }
            }
        });
        
        // Add hover effect visual feedback
        card.style.cursor = 'pointer';
    });
});
