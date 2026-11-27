<?php
/**
 * The link preview, on our pages only.
 *
 * What a pasted link looks like in WhatsApp, Facebook, LinkedIn or Slack is
 * decided entirely here. Left alone, WordPress gives these pages their own
 * defaults, and on this install those read "knackextra - Admin" with no
 * description at all, because the site's own Site Title is "Admin".
 *
 * The title and description come from inc/meta.php, which is generated from
 * index.html and policies.html, so they match what the page actually says and
 * do not depend on anybody remembering to fix Settings, General.
 *
 * Everything is skipped when an SEO plugin is active, so nothing is printed
 * twice and the plugin stays in charge.
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
 * Title and description for the current template.
 *
 * @return array
 */
function ke_current_meta() {
	$all  = ke_meta();
	$slug = ke_current_template();
	return isset( $all[ $slug ] ) ? $all[ $slug ] : array( 'title' => '', 'desc' => '' );
}

/**
 * Give these pages their own <title>.
 *
 * The site is called "Admin" in Settings, General, which WordPress appends to
 * every page title. These two pages say what they are instead.
 *
 * @param string $title The title WordPress built.
 * @return string
 */
function ke_document_title( $title ) {
	if ( ! ke_is_ours() || ke_seo_plugin_active() ) {
		return $title;
	}
	$meta = ke_current_meta();
	return $meta['title'] ? $meta['title'] : $title;
}
add_filter( 'pre_get_document_title', 'ke_document_title', 20 );

/**
 * Print the description and the sharing tags.
 *
 * No canonical is printed: WordPress core already emits one for a page, and a
 * second would be a duplicate.
 */
function ke_meta_tags() {
	if ( ! ke_is_ours() || ke_seo_plugin_active() ) {
		return;
	}

	$meta  = ke_current_meta();
	$title = $meta['title'] ? $meta['title'] : wp_get_document_title();
	$desc  = $meta['desc'];
	$url   = get_permalink();

	// A JPEG, not the WebP the page itself uses. WhatsApp copes with WebP, but
	// LinkedIn and X are unreliable with it, and a share card is not the place
	// to find that out.
	$image = ke_asset( 'img/share-card.jpg' );
	$file  = KNACK_DIR . 'assets/img/share-card.jpg';
	$dims  = file_exists( $file ) ? @getimagesize( $file ) : false;

	$tags = array(
		array( 'name', 'description', $desc ),
		array( 'property', 'og:type', 'website' ),
		array( 'property', 'og:site_name', 'Knack Extra' ),
		array( 'property', 'og:title', $title ),
		array( 'property', 'og:description', $desc ),
		array( 'property', 'og:url', $url ),
		array( 'property', 'og:locale', 'en_NG' ),
		array( 'property', 'og:image', $image ),
		array( 'property', 'og:image:alt', 'A bottle of Knack Extra Capsules.' ),
		array( 'name', 'twitter:card', 'summary_large_image' ),
		array( 'name', 'twitter:title', $title ),
		array( 'name', 'twitter:description', $desc ),
		array( 'name', 'twitter:image', $image ),
	);

	// Stating the size lets a scraper lay the card out without fetching the
	// image first, which is the difference between a preview appearing at once
	// and appearing a second later, or not at all on a slow connection.
	if ( $dims ) {
		$tags[] = array( 'property', 'og:image:type', $dims['mime'] );
		$tags[] = array( 'property', 'og:image:width', (string) $dims[0] );
		$tags[] = array( 'property', 'og:image:height', (string) $dims[1] );
	}

	foreach ( $tags as $tag ) {
		list( $attr, $key, $value ) = $tag;
		if ( '' === $value || null === $value ) {
			continue;
		}
		$is_url = in_array( $key, array( 'og:url', 'og:image', 'twitter:image' ), true );
		printf(
			'<meta %s="%s" content="%s">' . "\n",
			esc_attr( $attr ),
			esc_attr( $key ),
			$is_url ? esc_url( $value ) : esc_attr( wp_strip_all_tags( $value ) )
		);
	}
}
add_action( 'wp_head', 'ke_meta_tags', 3 );
