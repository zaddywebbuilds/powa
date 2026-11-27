<?php
/**
 * Canonical and sharing tags, on our pages only.
 *
 * Skipped entirely when an SEO plugin is active, so nothing is printed twice
 * and the plugin stays in charge.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Is another plugin already handling this?
 *
 * @return bool
 */
function ke_seo_plugin_active() {
	return defined( 'WPSEO_VERSION' )
		|| class_exists( 'RankMath' )
		|| defined( 'AIOSEO_VERSION' )
		|| defined( 'SEOPRESS_VERSION' );
}

/**
 * Print canonical and Open Graph tags.
 */
function ke_meta_tags() {
	if ( ! ke_is_ours() || ke_seo_plugin_active() ) {
		return;
	}

	$url   = get_permalink();
	$title = wp_get_document_title();
	$desc  = get_the_excerpt();
	if ( ! $desc ) {
		$desc = get_bloginfo( 'description' );
	}

	printf( '<link rel="canonical" href="%s">' . "\n", esc_url( $url ) );
	printf( '<meta name="description" content="%s">' . "\n", esc_attr( wp_strip_all_tags( $desc ) ) );
	printf( '<meta property="og:type" content="website">' . "\n" );
	printf( '<meta property="og:site_name" content="%s">' . "\n", esc_attr( get_bloginfo( 'name' ) ) );
	printf( '<meta property="og:title" content="%s">' . "\n", esc_attr( $title ) );
	printf( '<meta property="og:description" content="%s">' . "\n", esc_attr( wp_strip_all_tags( $desc ) ) );
	printf( '<meta property="og:url" content="%s">' . "\n", esc_url( $url ) );
	printf( '<meta property="og:image" content="%s">' . "\n", esc_url( ke_asset( 'img/hero-dark.webp' ) ) );
	printf( '<meta property="og:locale" content="en_NG">' . "\n" );
	printf( '<meta name="twitter:card" content="summary_large_image">' . "\n" );
}
add_action( 'wp_head', 'ke_meta_tags', 3 );
