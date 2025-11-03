
## Returns help text for fields. The output is Markdown and needs to be rendered as such
def getDatabaseHelp(field) -> str:

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
        case 'model.kitlocation':
            return """
            If you find that you have too many kits in too many locations, use this field to identify where
            in your stash the kit lives. It could a room name, a shelf number, or a dewey decimal concoction
            all your own. Whatever works for you!
            """
        case 'model.subjecttype':
            return """
            Is this model a scale model? A fantasy model? Something in between? Or is it purely for fun?
            """
        case 'model.final_disposition':
            return """
            I know this is tough subject. You have worked hard on your models. You are proud of your collection.
            But will your estate's executor have any ideas what to do with it all when you are gone? Use this part
            of the form to share your wishes with your family. And help them understand a reasonable value for the
            model if they choose to collect any money from it. I have added a few friends' names to make sure 
            special models head their way (assuming, of course, my family doesn't want the item). Again, I know it
            is tough, but better you now then them later."""

        case 'component.diagramname':
            return """
            To keep the diagrams consice, use this field to output a shorter name for the component when it is part
            of a diagram. Maybe not as generic as 'servo', but maybe the model is unique enough that the manufacturer
            isn't necessary?
            """
        case 'component.componenttype':
            return """
            This is the main search field, as the list view is generated off this list. Adding a new type involves modifying
            the database, but this list is pretty complete. There is also a sub type field you can use to add more details
            (that is if the attributes aren't helpful enough.) This field also drives the editable list of attributes.
            """
        case 'component.storedat':
            return """
            If you have lots of components in lots of locations use this field to narrow down where you have to look.
            Maybe you have an upstairs room, or maybe you are organized enough to have numbered bins. Whatever work best
            for you is what is best to put in this field.
            """

            
        case _:
            return None