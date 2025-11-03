
def getDatabaseHelp(field) -> str:
    #print('-------------------')
    print(field.table, field.name)

    match f'{field.table}.{field.name}':
        case 'article.type':
            return """
            The article type is a high level category
            """
        case 'protocol.name':
            return """
            The name of the protocol is used in the UI to show which of             
            several protocols available on a 
            transmitter is actually used or can be used.
            """
        
        case 'transmitter.nickname':
            return """
            The nickname of the transmitter is used in the UI when limited 
            space is available. You may opt for a unique name or just a shortened 
            version of the transmitter's model.
            """

        case 'transmitter.os':
            return """
            The operating system of the transmitter really only applies to newer
            computer radios, but plays a significant role in understanding the 
            capabilities of a transmitter. I suggest incuding version information
            in this field as well due to the significant differences often found in
            different versions.
            """

        case 'transmitter.protocol':
            return """
            Newer computer radios often have the ability to speak in one or more protocols. 
            Use this field to identify all the protocols your transmitter can speak. New
            protocols can be added if necessary.
            """
        case 'model.modelorigin':
            return """
            How did this model first start out from your perspective? Did you draw it from
            scratch? What is an ARF? Was it something else?
            """
        case 'model.modelstate':
            return """
            The model's state is normally set by the flowchart while viewing the details of the model, 
            but it can be set here as well. The default state is 'Idea' which I use for straight up
            ideas - though using the Wishlist or Library is probably better - or for kits that are not
            started. Occationally I use 'Idea' for models I have gotten used as well, but have not started
            to work on. The other states are straightforward, though I would not suggest setting 'Retired/Disposed'
            from here unless you know there are no other associated records. To 'retire' a model, use the button
            on the detail page
            """
        case 'model.modelcategory':
            return """
            The Category of the model is a primary filter in the UI. It defaults views and editable fields
            based on whether the model is meant for RC, static display, or something that isn't a model.
            I use the Non-Model category for documenting my charging case. A trailer setup is another good 
            use of that category.
            """
        case 'model.haveplans' | 'model.havekit':
            return """
            Flagging if you have the plans or the kit allows filtering on those attributes. I also suggest
            checking 'Have kit/model' for already built models to, again, enable that filtering. I oftentimes
            put potential models and other ideas in as models so I don't have plans or a kit. Though, it is better
            to put pure ideas in the Wishlist or in the Library.
            """
        case _:
            return None