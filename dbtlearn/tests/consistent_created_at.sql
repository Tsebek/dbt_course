SELECT
    *
FROM {{ ref('fct_reviews') }} fct_reviews
  JOIN {{ ref('dim_listings_cleansed') }} dim_listings
    ON fct_reviews.listing_id = dim_listings.listing_id
      AND fct_reviews.review_date < dim_listings.created_at