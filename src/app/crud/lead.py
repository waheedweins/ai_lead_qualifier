def create_lead(db: Session, lead: LeadCreate) -> Lead:
    """
    Creates a new lead record. Ensure field names match the Lead model.
    """
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        title=lead.title,      # Ensure this matches LeadCreate schema
        address=lead.address   # Ensure this matches LeadCreate schema
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
