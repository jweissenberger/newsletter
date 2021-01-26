jQuery( document ).ready( function( jQuery ) {

	'use strict';

	// For Scroll to top
	if ( jQuery( '#bg-to-top' ).length ) {
		jQuery( window ).on( 'scroll resize', function() {
			if ( jQuery( window ).scrollTop() >= 900 ) {
				jQuery( '#bg-to-top' ).css( 'bottom', '1rem' );
			}
			if ( jQuery( window ).scrollTop() < 900 ) {
				jQuery( '#bg-to-top' ).css( 'bottom', '-5rem' );
			}
		} );

		jQuery( '#bg-to-top' ).click( function() {
			jQuery( 'html, body' ).animate( { scrollTop: 0 }, 'slow' );
			return false;
		} );
	}

} );
